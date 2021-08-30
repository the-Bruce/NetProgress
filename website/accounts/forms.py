from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.forms import ModelForm, PasswordInput
from django.template import loader

from .models import Member
from progress.email import generate_email_body


class MemberForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Monkeypatch the following fields to be required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = Member
        fields = ['username','first_name', 'last_name', 'email']


class SignupForm(ModelForm):
    class Meta:
        model=Member
        fields=['username', 'email', 'password']
        widgets = {
            'password': PasswordInput()
        }


class PasswordResetFormPremailer(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        if html_email_template_name is not None:
            body, html_email = generate_email_body(context, email_template_name, html_email_template_name)
            email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
        else:
            body = loader.render_to_string(email_template_name, context)
            email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
            email_message.send()
