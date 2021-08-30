from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetConfirmView, \
    PasswordResetView
from django.views import View
from django.contrib.messages import add_message
from django.contrib import messages
from django.urls import reverse_lazy, reverse

# Create your views here.
from django.views.generic import ListView, FormView

from .forms import MemberForm, PasswordResetFormPremailer, SignupForm
from .models import Member


class Login(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True  # A very slight privacy risk. Negligible for our site...

    def form_valid(self, form):
        add_message(self.request, messages.SUCCESS, "Successfully logged in!")
        return super().form_valid(form)


class Logout(LogoutView):
    next_page = reverse_lazy("homepage")

    def get_next_page(self):
        add_message(self.request, messages.SUCCESS, "Successfully logged out!")
        return super().get_next_page()


class ChangePassword(PasswordChangeView):
    def get_success_url(self):
        add_message(self.request, messages.SUCCESS, "Password Changed")
        return reverse("accounts:edit")


class PasswordResetConfirm(PasswordResetConfirmView):
    def get_success_url(self):
        add_message(self.request, messages.SUCCESS, "Password Reset Successfully")
        return reverse("accounts:login")


class PasswordReset(PasswordResetView):
    html_email_template_name = "registration/password_reset_html_email.html"
    form_class = PasswordResetFormPremailer

    def get_success_url(self):
        return reverse("accounts:password_reset_done")


class Signup(FormView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("dashboard:dashboard")

    def form_valid(self, form):
        Member.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
        auth = authenticate(self.request, username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
        if auth is None:
            raise RuntimeError("Impossible state reached")
        login(self.request, auth)
        return super().form_valid(form)


class Edit(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'memberform': MemberForm(instance=request.user),
        }
        return render(request, 'accounts/edit.html', context)

    def post(self, request):
        # generate a filled form from the post request
        memberform = MemberForm(request.POST, instance=request.user)
        if memberform.is_valid():
            memberform.save()
            add_message(request, messages.SUCCESS, "Profile successfully updated.")
            return HttpResponseRedirect(reverse('homepage'))
        else:
            context = {
                'memberform': memberform,
            }
            return render(request, 'accounts/edit.html', context)