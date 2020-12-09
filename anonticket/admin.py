from django.contrib import admin

# Register your models here.

from .models import Project, Issue, UserIdentifier
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(UserIdentifier)