from django.urls import path, include
from django.views.generic import TemplateView, DetailView, ListView
from . import views
from django.conf import settings
from anonticket.views import (
    CreateIdentifierView, 
    IssueSuccessView,
    UserLoginErrorView,
    ProjectListView,
    ProjectDetailView,
    PendingIssueDetailView,
    )


urlpatterns = [
    path('', TemplateView.as_view(template_name="anonticket/index.html"), name='home'),
    path('user/create_identifier/', views.CreateIdentifierView.as_view(), name='create-identifier'),
    path('user/login/', views.login_view, name='login'),
    path('user/<str:user_identifier>/login_error/', views.UserLoginErrorView.as_view(), name='user-login-error'),
    path('user/<str:user_identifier>/create_issue/success/', views.IssueSuccessView.as_view(), name='issue-created'),        
    path('user/<str:user_identifier>/create_issue/', views.create_issue_view, name='create-issue'),
    path('user/<str:user_identifier>/projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('user/<str:user_identifier>/projects/', views.ProjectListView.as_view(), name='project-list'),
    path('user/<str:user_identifier>/issue/<int:project_id>/<int:issue_iid>/details/', views.issue_detail_view, name='issue-detail-view'),
    path('user/<str:user_identifier>/issue/pending/<int:project_id>/<int:pk>/details/', views.PendingIssueDetailView.as_view(), name='pending-issue-detail-view'),
    path('user/<str:user_identifier>/search/', views.issue_search_view, name="issue-search"),
    path('user/<str:user_identifier>/', views.user_landing_view, name='user-landing'),
]