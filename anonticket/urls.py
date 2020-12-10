from django.urls import path, include
from . import views
from django.conf import settings
from django.views.generic import TemplateView
from anonticket.views import CreateIdentifier


urlpatterns = [
    path('', TemplateView.as_view(template_name="anonticket/index.html"), name='home'),
    path('search_by_id/', views.search_by_id, name="search-by-id"),
    path('create_issue/', views.create_issue, name="create-issue"),
    path('save_issue/', views.save_issue, name="save-issue"),
    path('create_identifier/', views.CreateIdentifier.as_view(), name='create-identifier')
]