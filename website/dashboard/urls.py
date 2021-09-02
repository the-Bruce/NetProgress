from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("dash/", views.Dashboard.as_view(), name='dashboard'),
    path("clear_runs/", views.ClearRuns.as_view(), name='delete_runs'),
    path("new_project/", views.CreateProject.as_view(), name='create_project'),
    path("api/status/", views.Status.as_view(), name='status'),
    path("api/update/", views.Update.as_view(), name='update'),
    path("api/init/", views.Init.as_view(), name='init'),

]