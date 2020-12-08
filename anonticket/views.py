from django.shortcuts import render, redirect
from .forms import (
    Anonymous_Ticket_Project_Search_Form, 
    Create_Anonymous_Issue_Form,
    Save_Anonymous_Ticket,
    Generate_User_Identifier_Form)
from anonticket.models import Issue, AnonUser

def search_by_id(request):
    results = {}
    if 'issue_iid' in request.GET:
        form = Anonymous_Ticket_Project_Search_Form(request.GET)
        if form.is_valid():
            results = form.call_project_and_issue()
    else:
        form = Anonymous_Ticket_Project_Search_Form
    return render(request, 'anonticket/search_by_id.html', {'form': form, 'results': results})

def create_issue(request):
    results = {}
    if 'description_of_issue' in request.GET:
        form = Create_Anonymous_Issue_Form(request.GET)
        if form.is_valid():
            results = form.create_issue()
    else:
        form = Create_Anonymous_Issue_Form
    return render(request, 'anonticket/create_issue.html', {'form': form, 'results': results})

def save_issue(request):
    form = Save_Anonymous_Ticket
    # Check if this is a POST request. If so, process the form data.
    if request.method == 'POST':
        form = Save_Anonymous_Ticket(request.POST)
        #Check if form is valid:
        if form.is_valid():
            working_issue = form.save()
            return redirect('home')
    else: 
        form = Save_Anonymous_Ticket
    return render(request, 'anonticket/save_issue.html', {'form': form})

def create_identifier(request):
    # Check to see if this is a GET request. If so, run the method. If not
    results = {}
    form  = Generate_User_Identifier_Form(request.GET)
    results = form.get_user_identifer()
    return render(request, 'anonticket/get_identifier.html', {'form': form, 'results': results})