"""ticketlobby URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ratelimit.exceptions import Ratelimited
from django.http import HttpResponse
from django.shortcuts import redirect

def handler403(request, exception=None):
    """Custom 403 handler for ratelimit exceptions."""
    response_message = """This ticket has failed due to too many requests in
    a short period of time. If you like, you can hit the "back" button to return
    to your form. Your data should still be filled in. You can then 
    wait and retry creating your ticket."""
    if isinstance(exception, Ratelimited):
        return HttpResponse(response_message, status=403)
    return HttpResponseForbidden('Forbidden')

urlpatterns = [
    path('tor_admin/', admin.site.urls),
    path('', include('anonticket.urls'))
]

