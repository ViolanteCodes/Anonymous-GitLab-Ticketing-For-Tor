from django.shortcuts import render, redirect
from django.conf import settings
import gitlab
from anonticket.models import Issue, UserIdentifier
from .forms import (
    Anonymous_Ticket_Project_Search_Form, 
    LoginForm,
    CreateIssueForm)
from django.views.generic.base import TemplateView

# These views have been listed below in the order that a user is likely 
# to encounter them, e.g., create an identifier, login, create an issue. 

class CreateIdentifierView(TemplateView):
    """Class-based view that randomly samples a word_list and passes the
    new user_identifier into a context dictionary for the template, 
    including a string version and a link."""

    template_name = "anonticket/create_identifier.html"
    
    def get_wordlist(self): 
        """Fetches the wordlist."""
        # Pull the path for the wordlist from django settings
        word_list_path = settings.WORD_LIST_PATH
        with open(word_list_path) as f:
            wordlist_as_list = f.read().splitlines()
            return wordlist_as_list

    def generate_user_identifier_list(self, word_list=[]):
        """Randomly samples X words from word_list."""
        # Import the random module
        import random
        # Use random.sample to pull x words from word_list, where number of 
        # dice is = to settings.DICE_ROLLS. 
        user_list = random.sample(word_list, settings.DICE_ROLLS)
        return user_list

    def context_dict(self, word_list=[]):
        """Build the context dictionary."""
        context = {}
        # pass the wordlist into the context dictionary with key 'chosen_words'
        context['chosen_words'] = word_list
        join_character = '-'
        # Join the list with join_character and save as user_identifier_string
        user_identifer_string = join_character.join(word_list)
        # Pass the string into the context dictionary
        context['user_identifier_string'] = user_identifer_string
        # return context dictionary to use in template
        return context

    def get_context_data(self):
        """Fetch wordlist, pull out words at random, convert to dictionary
        for rendering in django template."""
        # Call the get_wordlist function and save as word_list
        word_list = self.get_wordlist()
        # Call the generate_user_identifier_list function and save as chosen_words
        chosen_words = self.generate_user_identifier_list(word_list=word_list)
        # Call the function that generates the context dictionary to return to template.
        context = self.context_dict(word_list=chosen_words)
        return context

def login_with_codename(request):
    """Generate a form with fields to allow users to enter their codename. If all
    fields are filled out, redirect to appropriate user-landing."""
    results = {}
    form = LoginForm(request.GET)
    # if the LoginForm is filled out, clean data and join the words together 
    # using the forms join_words function (defined in the form.)
    if form.is_valid():
        results = form.join_words()
        # redirect to user-landing view, passing results dictionary as kwarg
        return redirect('user-landing', user_identifier = results)
    # if no valid post request, display the form
    else: 
        form = LoginForm
    return render (request, 'anonticket/user_login.html', {'form':form, 'results': results})
    
class UserLandingView(TemplateView):
    """The user 'landing page' once they have chosen an identifier and
    decided to use it. Checks if identifier is in database and offers 
    options to the user, e.g., create ticket, etc. """

    template_name = "anonticket/user_landing.html"

    def user_identifier_in_database(self, find_user):
        """See if user_identifier is in database."""

        user_not_found_message = """Nothing to see here! You have
        either not taken an action, or this is not a valid code-phrase."""
        user_found_flag = False
        
        # Try to find the user in the database.
        try:
            find_user = UserIdentifier.objects.get(user_identifier=find_user)
            # if found, update the user_found message
            user_found = """Code-phrase Found! You have taken the following actions:"""
            user_found_flag = True

        except:
            # if user is not found, return user_not_found message
            user_found = user_not_found_message
        return user_found

    def get_context_data(self, *args, **kwargs):
        # defines specific methods in how this TemplateView creates context
        context = super().get_context_data(**kwargs)
        # pass this user_identifier kwarg into variable user_identifier
        user_identifier = kwargs['user_identifier']
        # run the user_identifier_in_database method using the user_identifier variable
        user_found = self.user_identifier_in_database(find_user=user_identifier)
        context['user_found'] = user_found
        return context

def create_issue(request, user_identifier):
    """View that allows a user to create an issue. Pulls the user_identifier
    from the URL(kwargs) and tries to pull that UserIdentifier from database, 
    creating it if this is the user's first action."""
    results = {}
    user_to_retrieve = user_identifier
    if request.method == 'POST':
        form = CreateIssueForm(request.POST)
        if form.is_valid():
            # Create the issue, but don't save it yet, since we need to get
            # the user_identifier.
            issue_without_user = form.save(commit=False)
            # Add the user_identifier to the context dictionary to be passed to
            # redirect upon success.
            results['user_identifier'] = user_identifier
            # Try to find the user_identifier in database. 
            try: 
                current_user = UserIdentifier.objects.get(user_identifier=user_to_retrieve)
            # If lookup fails, create the user.
            except: 
                current_user = UserIdentifier(user_identifier=user_to_retrieve)
                current_user.save()
            # Assign the user_identifer to the issue and then same the issue. 
            issue_without_user.linked_user = current_user
            # Save the new issue. 
            issue_without_user.save()
            return redirect('issue-created', user_identifier)
    else:
        form = CreateIssueForm
    return render(request, 'anonticket/create_issue.html', {'form':form, 'results':results})

class IssueSuccessView(TemplateView):
    """View that tells the user their issue was successfully created."""

    template_name = 'anonticket/issue_created_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def search_by_id(request):
    """Currently admin-function to allow someone to lookup an issue and its notes
    given a project and issueiid"""
    results = {}
    if 'issue_iid' in request.GET:
        form = Anonymous_Ticket_Project_Search_Form(request.GET)
        if form.is_valid():
            results = form.call_project_and_issue()
    else:
        form = Anonymous_Ticket_Project_Search_Form
    return render(request, 'anonticket/search_by_id.html', {'form': form, 'results': results})

