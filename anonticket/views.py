from django.shortcuts import render, redirect
from django.conf import settings
import gitlab
import random
from .forms import (
    Anonymous_Ticket_Project_Search_Form, 
    Create_Anonymous_Issue_Form,
    Save_Anonymous_Ticket)
from anonticket.models import Issue, UserIdentifier
from django.views.generic.base import TemplateView


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

class CreateIdentifier(TemplateView):
    """Class-based view that randomly samples a word_list and passes the
    new user_identifier into a context dictionary for the template, 
    including a string version and a link."""

    template_name = "anonticket/create_identifier.html"
    
    def get_wordlist(self): 
        """Fetches the wordlist."""
        word_list_path = settings.WORD_LIST_PATH
        with open(word_list_path) as f:
            wordlist_as_list = f.read().splitlines()
            return wordlist_as_list

    def generate_user_identifier_list(self, word_list=[]):
        """Randomly samples X words from word_list where X is equal
        to settings.DICE_ROLLS and word_list is equal to settings.WORD_LIST_PATH."""
        user_list = random.sample(word_list, settings.DICE_ROLLS)
        return user_list

    def context_dict(self, word_list=[]):
        """Build the context dictionary."""
        context = {}
        context['chosen_words'] = word_list
        join_character = '-'
        user_identifer_string = join_character.join(word_list)
        context['user_identifier_string'] = user_identifer_string
        user_link = f"/{user_identifer_string}/"
        context['user_link'] = user_link
        return context

    def get_context_data(self):
        """Fetch wordlist, pull out words at random, convert to dictionary
        for rendering in django template."""
        word_list = self.get_wordlist()
        chosen_words = self.generate_user_identifier_list(word_list=word_list)
        context = self.context_dict(word_list=chosen_words)
        return context
    
def user_landing(request):
    """Check to see if the user_identifier string matches a User Identifier in database. If so, 
    route to user_identifier landing page. If not, route to a different page."""

