from django.urls import path, include, reverse
from django.views.generic import (
    TemplateView, DetailView, ListView, CreateView, UpdateView)
from . import views
from django.conf import settings
from anonticket.views import (
    CreateIdentifierView, 
    IssueSuccessView,
    ObjectCreatedNoUserView,
    UserLoginErrorView,
    GitlabAccountRequestCreateView,
    CannotCreateObjectView,
    ProjectListView,
    ProjectDetailView,
    PendingIssueDetailView,
    NoteCreateView,
    ModeratorNoteUpdateView,
    ModeratorIssueUpdateView,
    ModeratorGitlabAccountRequestUpdateView,
    )


urlpatterns = [
    path(
        '', 
        TemplateView.as_view(template_name="anonticket/index.html"), 
        name='home'),
    path(
        'user/create_identifier/', 
        views.CreateIdentifierView.as_view(), 
        name='create-identifier'),
    path(
        'user/login/', 
        views.login_view, name='login'),
    path(
        'user/gitlab-account/create/', 
        views.GitlabAccountRequestCreateView.as_view(), 
        name='create-gitlab-no-user'),
    path(
        'user/<str:user_identifier>/create-failed/', 
        views.CannotCreateObjectView.as_view(), 
        name='cannot-create-with-user'),
    path(
        'user/<str:user_identifier>/gitlab-account/create/', 
        views.GitlabAccountRequestCreateView.as_view(), 
        name='create-gitlab-with-user'),
    path(
        'user/<str:user_identifier>/login_error/', 
        views.UserLoginErrorView.as_view(), name='user-login-error'),
    path(
        'user/<str:user_identifier>/projects/<slug:project>/issues/<int:issue_iid>/notes/create/', 
        views.NoteCreateView.as_view(), 
        name='create-note'),
    path(
        'user/<str:user_identifier>/projects/<slug:project>/issues/<int:issue_iid>/notes/<int:pk>/', 
        views.PendingNoteDetailView.as_view(), name='pending-note'),
    path(
        'user/<str:user_identifier>/projects/<slug:project_slug>/issues/<int:gitlab_iid>/details/', 
        views.issue_detail_view, name='issue-detail-view'),
    path(
        'user/<str:user_identifier>/projects/<slug:project_slug>/issues/pending/<int:pk>/', 
        views.PendingIssueDetailView.as_view(), name='pending-issue-detail-view'),
    path(
        'user/<str:user_identifier>/projects/all/issues/search/', 
        views.issue_search_view, name="issue-search"),
    path(
        'user/<str:user_identifier>/projects/<slug:slug>/', 
        views.ProjectDetailView.as_view(), name='project-detail'),
    path(
        'user/<str:user_identifier>/projects/', 
        views.ProjectListView.as_view(), name='project-list'),
    path(
        'user/<str:user_identifier>/create/success/', 
        views.IssueSuccessView.as_view(), name='issue-created'),
    path(
        'user/create/success/', 
        views.ObjectCreatedNoUserView.as_view(), name='created-no-user'),         
    path(
        'user/<str:user_identifier>/create_issue/', 
        views.create_issue_view, name='create-issue'),
    path(
        'user/<str:user_identifier>/', 
        views.user_landing_view, name='user-landing'),
    path(
        'moderator/', 
        views.moderator_view, name='moderator'),
    path(
        'moderator/update-note/<int:pk>', 
        views.ModeratorNoteUpdateView.as_view(), 
        name='mod-update-note'),
    path(
        'moderator/update-issue/<int:pk>', 
        views.ModeratorIssueUpdateView.as_view(), 
        name='mod-update-issue'),
    path(
        'moderator/update-gitlab-account-request/<int:pk>', 
        views.ModeratorGitlabAccountRequestUpdateView.as_view(), 
        name='mod-update-gitlab-account-request'),
]