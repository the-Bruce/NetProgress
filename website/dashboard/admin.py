from django.contrib import admin

from .models import Project, Run, Bar

# Register your models here.
admin.site.register(Project)
admin.site.register(Run)
admin.site.register(Bar)
