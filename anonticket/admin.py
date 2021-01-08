from django.contrib import admin

# Register your models here.

from .models import UserIdentifier, GitLabGroup, Project, Issue
admin.site.register(UserIdentifier)
admin.site.register(GitLabGroup)
admin.site.register(Project)

def bulk_approve_issues(modeladmin, request, queryset):
    """Add a bulk approval method for issues to admin panel."""
    for issue in queryset:
        issue.reviewer_status = 'A'
        issue.save()

bulk_approve_issues.short_description = "Approve selected issues and post to GitLab."

@admin.register(Issue)
class IssueModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'linked_project','reviewer_status')
    list_filter = ('reviewer_status', )
    actions = [bulk_approve_issues]