from django.contrib import admin

# Register your models here.

from .models import Project, Issue, UserIdentifier
admin.site.register(Project)
admin.site.register(UserIdentifier)

@admin.register(Issue)
class IssueModelAdmin(admin.ModelAdmin):
    list_display = ('issue_title', 'linked_project','reviewer_status')