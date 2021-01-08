import gitlab
import functools
from django.conf import settings
from anonticket.models import UserIdentifier, GitLabGroup, Project, Issue
from .forms import (
    Anonymous_Ticket_Project_Search_Form, 
    LoginForm,
    CreateIssueForm)
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView, ListView

# ---------------SHARED FUNCTIONS, NON GITLAB---------------------------
# Functions that need to be accessed from within multiple views go here,
# with the exception of gitlab functions, which are below.
# ----------------------------------------------------------------------

# Set WORD_LIST_CONTENT as global variable with value of None.
WORD_LIST_CONTENT = None

def get_wordlist():
    """Returns the wordlist. If wordlist_as_list is not already in memory,
    fetches the wordlist from file and creates it."""
    global WORD_LIST_CONTENT
    if WORD_LIST_CONTENT is None:
        word_list_path = settings.WORD_LIST_PATH
        with open(word_list_path) as f:
            wordlist_as_list = f.read().splitlines()
    return wordlist_as_list  

def user_identifier_in_database(find_user):
    """See if user_identifier is in database. Returns True/False."""
    # Try to find the user in the database.
    try:
        user_to_find = UserIdentifier.objects.get(user_identifier=find_user)
        # if found, update the user_found message
        user_found = True
    except:
        # if user is not found, return user_not_found message
        user_found = False
    return user_found

def get_user_as_object(find_user):
    """Gets the User Identifier from the database. Should only be used if User Identifier exists."""
    user_to_find = UserIdentifier.objects.get(user_identifier=find_user)
    return user_to_find

def get_linked_issues(UserIdentifier):
    """Gets a list of the issues assigned to a User Identifier."""
    linked_issues = Issue.objects.filter(linked_user=UserIdentifier)
    return linked_issues

# --------------------DECORATORS AND MIXINS-----------------------------
# Django decorators wrap functions (such as views) in other functions. 
# Mixins perform a similar function for class based views.
# ----------------------------------------------------------------------

def validate_user(view_func):
    """A decorator that checks if a user_identifier matches validation requirements."""
    @functools.wraps(view_func)
    def validate_user_identifier(request, user_identifier, *args, **kwargs):
        user_string = user_identifier
        id_to_test = user_string.split('-')
    # Check that code-phrase length is equal to settings.DICE_ROLLS
        if len(id_to_test) != settings.DICE_ROLLS:
            return redirect('user-login-error', user_identifier=user_string)
    # Check that all words in code-phrase are unique
        set_id_to_test = set(id_to_test)
        if len(set_id_to_test) != len(id_to_test):
            return redirect('user-login-error', user_identifier=user_string)
    # Grab the word_list from the path specified in settings.py
        wordlist_as_list = get_wordlist()
    # Check that all words are in the dictionary.
        check_all_words  = all(item in wordlist_as_list for item in id_to_test)
        if check_all_words == False:
            return redirect('user-login-error', user_identifier=user_string)
        else:
            response = view_func(request, user_identifier, *args, **kwargs)
        return response
    return validate_user_identifier

def validate_project_in_database(view_func):
    """A decorator for URL validation that checks if a project is in the database."""
    @functools.wraps(view_func)
    def check_project(request, user_identifier, gitlab_id, *args, **kwargs):
        try:
            get_object_or_404(Project, gitlab_id=gitlab_id)
        except:
            return redirect('home')
        response = view_func(request, user_identifier, gitlab_id, *args, **kwargs)
        return response
    return check_project

class PassUserIdentifierMixin:
    """Mixin that passes user_identifier from CBV kwargs to view
    context in a 'results' dictionary, which allows it to be called in template
    with results.user_identifier (same as FBV)."""

    def get_context_data(self, **kwargs):          
        context = super().get_context_data(**kwargs)
        context['results'] = {'user_identifier':self.kwargs['user_identifier']}                     
        return context

# ------------------SHARED FUNCTIONS, GITLAB---------------------------
# Easy to parse version of GitLab-Python functions.
# ----------------------------------------------------------------------
gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_SECRET_TOKEN)

def gitlab_get_project(project):
    """Takes an integer, and grabs a gitlab project where gitlab_id
    matches the integer."""
    working_project = gl.projects.get(project)
    return working_project

def gitlab_get_issue(project, issue):
    """Takes two integers and grabs corresponding gitlab issue."""
    working_project = gitlab_get_project(project)
    working_issue = working_project.issues.get(issue)
    return working_issue

def gitlab_get_notes_list(project, issue):
    """Grabs the notes list for a specific issue."""
    working_issue = gitlab_get_issue(project, issue)
    notes_list = working_issue.notes.list()
    return notes_list

def gitlab_get_issues_list(project):
    """Grabs the issues list for a specific project."""
    working_project = gitlab_get_project(project)
    issues_list = working_project.issues.list()
    return issues_list

# --------------------------SPECIFIC VIEWS------------------------------
# The functions below are listed in the order that a user is likely to 
# encounter them (e.g., generate a codename, then login with codename.)
# ----------------------------------------------------------------------
#
# --------------------IDENTIFIER AND LOGIN VIEWS------------------------
# Initial views related to landing, user_identifier.
# ----------------------------------------------------------------------

class CreateIdentifierView(TemplateView):
    """View that randomly samples a word_list and passes the
    new user_identifier as string into a context dictionary."""

    template_name = "anonticket/create_identifier.html"
    
    def generate_user_identifier_list(self):
        """Randomly samples X words from word_list."""
        # Import the random module
        import random
        word_list = get_wordlist()
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
        user_identifier_string = join_character.join(word_list)
        # Pass the string into the context dictionary
        context['user_identifier_string'] = user_identifier_string
        # return context dictionary to use in template
        return context

    def get_context_data(self):
        """Fetch wordlist, pull out words at random, convert to dictionary
        for rendering in django template."""
        # Call the get_wordlist function and save as word_list
        word_list = get_wordlist()
        # Start a while loop
        while True:
        # Call the generate_user_identifier_list function and save as chosen_words
            chosen_words = self.generate_user_identifier_list()
            # Call the function that generates the context dictionary to return to template.
            context = self.context_dict(word_list=chosen_words)
            # Check if user already exists in the database
            user_found = user_identifier_in_database(context['user_identifier_string'])
            # if user is unique, return the context dictionary to the template and render
            if user_found == False:
                return context
            # if user is not unique, re-enter the loop
            else: 
                continue

def login_view(request):
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

@validate_user
def user_landing_view(request, user_identifier):
    """The 'landing page'. Checks if user_identifier is in database and 
    passes user_found = True to context dictionary if found, along
    with any issues or comments created by user."""
    results = {}
    # Check that entered User Identifier meets validation
    user_found = user_identifier_in_database(user_identifier)
    # if user is found, pass 'user_found' to context dictionary
    if user_found == True:
        results['user_found'] = user_found
        # Get linked issues linked to this user identifier and pass into 
        # results dictionary.
        working_user = get_user_as_object(user_identifier)
        linked_issues = get_linked_issues(working_user)
        results['linked_issues'] = linked_issues        
    # if found or not found, pass 'user_identifier' to context dictionary
    results['user_identifier'] = user_identifier
    return render(request, 'anonticket/user_landing.html', {'results': results})

class UserLoginErrorView(TemplateView):
    """A generic landing page if a username doesn't pass validation tests."""
    template_name = 'anonticket/user_login_error.html'

# -------------------------PROJECT VIEWS----------------------------------
# Views related to creating/looking up issues.
# ----------------------------------------------------------------------

@method_decorator(validate_user, name='dispatch')
class ProjectListView(PassUserIdentifierMixin, ListView):
    """Simple List View of all projects."""
    queryset = Project.objects.order_by('name_with_namespace')

@method_decorator(validate_user, name='dispatch')
class ProjectDetailView(DetailView):
    """A detail view of a single project."""
    model = Project

    def get_context_data(self, **kwargs):          
        context = super().get_context_data(**kwargs)
        context['results'] = {'user_identifier':self.kwargs['user_identifier']}                     
        project_slug = self.kwargs['slug']
        working_project = Project.objects.get(
            slug=project_slug
        )
        working_id = working_project.gitlab_id
        gitlab_project = gl.projects.get(working_id)
        issues_list = gitlab_project.issues.list()
        context['issues_list'] = issues_list                   
        return context
    
# -------------------------ISSUE VIEWS----------------------------------
# Views related to creating/looking up issues.
# ----------------------------------------------------------------------

@validate_user
def create_issue_view(request, user_identifier):
    """View that allows a user to create an issue. Pulls the user_identifier
    from the URL path and tries to pull that UserIdentifier from database, 
    creating it if this is the user's first action."""
    results = {}
    results['user_identifier'] = user_identifier
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
            # Assign the user_identifier to the issue and then same the issue. 
            issue_without_user.linked_user = current_user
            # Save the new issue. 
            issue_without_user.save()
            return redirect('issue-created', user_identifier)
    else:
        form = CreateIssueForm
    return render(request, 'anonticket/create_new_issue.html', {'form':form, 'results':results})

@method_decorator(validate_user, name='dispatch')
class IssueSuccessView(PassUserIdentifierMixin, TemplateView):
    """View that tells the user their issue was successfully created."""
    template_name = 'anonticket/create_issue_success.html'

@method_decorator(validate_user, name='dispatch')
class PendingIssueDetailView(PassUserIdentifierMixin, DetailView):
    """View for pending issues that have not been mod approved."""
    model = Issue
    template_name = 'anonticket/issue_pending.html'

@validate_user
@validate_project_in_database
def issue_detail_view(request, user_identifier, gitlab_id, gitlab_iid):
    """Detailed view of an issue that has been approved and posted to GL."""
    # Attempt to fetch the project from the database. If project is not in 
    # database, redirect.
    results = {}
    results['user_identifier']=user_identifier
    working_project = gitlab_get_project(project=gitlab_id)
    results['project'] = working_project.attributes
    working_issue = gitlab_get_issue(project=gitlab_id, issue=gitlab_iid)
    results['issue'] = working_issue.attributes
    results['notes'] = []
    notes_list = gitlab_get_notes_list(project=gitlab_id, issue=gitlab_iid)
    for note in notes_list:
        note_dict = note.attributes
        results['notes'].append(note_dict)
    results['notes'].reverse()
    return render(request, 'anonticket/issue_detail.html', {'results': results})

@validate_user
def issue_search_view(request, user_identifier):
    """Allows a user to select a project and search Gitlab for issues matching
    a search string."""
    results = {}
    if 'search_terms' in request.GET:
        form = Anonymous_Ticket_Project_Search_Form(request.GET)
        if form.is_valid():
            results = form.call_project_and_issue()
            results['user_identifier'] = user_identifier
    else:
        form = Anonymous_Ticket_Project_Search_Form
        results['user_identifier'] = user_identifier
    return render(request, 'anonticket/issue_search.html', {'form': form, 'results': results})

