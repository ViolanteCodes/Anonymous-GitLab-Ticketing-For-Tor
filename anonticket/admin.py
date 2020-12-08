from django.contrib import admin

# Register your models here.

from .models import Project, Issue
admin.site.register(Project)
admin.site.register(Issue)