import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import add_message
from django.contrib.messages import constants as message
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView

# Create your views here.
from dashboard.models import Project, Bar, Run
from progress.utils import JsonView


def home(request):
    return render(request, "base.html")


class Dashboard(LoginRequiredMixin, ListView):
    model = Project
    template_name = "dashboard/dashboard.html"
    context_object_name = "project_list"

    def get_context_data(self, *args, **kwargs):
        ctxt = super().get_context_data(*args, **kwargs)
        ctxt['ts'] = timezone.now().isoformat()
        return ctxt

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class ClearRuns(LoginRequiredMixin, View):
    def post(self, request):
        if 'id' not in request.POST:
            add_message(request, message.ERROR, "Error. Malformed request.")
        else:
            try:
                project = Project.objects.get(id=request.POST['id'])
                project.run_set.all().delete()
                add_message(request, message.SUCCESS, "Runs cleared.")
            except Project.DoesNotExist:
                add_message(request,  message.ERROR, "Error. Invalid project ID.")
        return HttpResponseRedirect(reverse("dashboard:dashboard"))


class CreateProject(LoginRequiredMixin, CreateView):
    model = Project
    template_name = "dashboard/create.html"
    fields = ['name']
    success_url = reverse_lazy("dashboard:dashboard")

    def form_valid(self, form):
        form.instance.user=self.request.user
        response = super().form_valid(form)
        return response


class Status(LoginRequiredMixin, JsonView):
    def get_data(self, context):
        if 'since' not in self.request.GET:
            return {"error": True, "error_reason": "Missing Required Field"}
        data = {
            "ts": timezone.now().isoformat()
        }
        updates = {}
        for i in Bar.objects.filter(last_change__gt=self.request.GET['since'], run__project__user=self.request.user):
            updates[i.id] = {'val': i.current, 'perc': i.percent}
            if i.complete:
                updates[i.id]["comp"] = True
            if i.errored:
                updates[i.id]["err"] = True
        data['u'] = updates
        new = {}
        for i in Bar.objects.filter(start_time__gt=self.request.GET['since'], run__project__user=self.request.user):
            new[i.id] = {'name': i.name, 'val': i.current, 'max': i.maxval, 'perc': i.percent, 'run': i.run_id,
                         'comp': i.complete, 'err': i.errored, 'id': i.id}
        if new:
            data['new'] = new
        runs = {}
        for i in Run.objects.filter(start_date__gt=self.request.GET['since'], project__user=self.request.user):
            runs[i.id] = i.project_id
        if runs:
            data['runs'] = runs
        return data


@method_decorator(csrf_exempt, name='dispatch')
class Init(View):
    def post(self, request):
        if 'key' not in request.POST:
            return JsonResponse({'error': "Missing API Key"}, status=400)
        project = Project.objects.get(apikey=request.POST['key'])
        run = Run.objects.create(project=project)
        return JsonResponse({'key': run.apikey})


@method_decorator(csrf_exempt, name='dispatch')
class Update(View):
    def post(self, request):
        print(request.POST)
        if 'key' not in request.POST:
            return JsonResponse({'error': "Missing API Key"}, status=400)
        if 'updates' not in request.POST:
            return JsonResponse({'error': "Missing Required Field"}, status=400)
        try:
            updates = json.loads(request.POST['updates'])
        except json.JSONDecodeError:
            return JsonResponse({'error': "Malformed Request"}, status=400)

        try:
            run = Run.objects.get(apikey=request.POST['key'])
        except Run.DoesNotExist:
            return JsonResponse({'error': "Invalid API Key"}, status=400)

        bars = run.bar_set.all()
        for k, i in updates.items():
            bar, new = bars.get_or_create(name=k, defaults={'maxval': 100, 'current': 0, 'run_id': run.id})
            if 'max' in i:
                bar.maxval = int(i['max'])
            if 'done' in i:
                bar.complete = bool(i['done'])
            if 'error' in i:
                bar.errored = bool(i['error'])
            if 'val' in i:
                bar.current = int(i['val'])
            print(i, bar)
            bar.save()

        return HttpResponse(status=204)
