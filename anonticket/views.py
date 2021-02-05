import gitlab
import functools
from django.conf import settings
from anonticket.models import (
    UserIdentifier, Project, Issue, Note, GitlabAccountRequest)
from .forms import (
    Anonymous_Ticket_Project_Search_Form, 
    LoginForm,
    CreateIssueForm,
    )
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import (
    TemplateView, DetailView, ListView, CreateView, FormView, UpdateView)
from django.contrib.admin.views.decorators import staff_member_required

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

def get_linked_notes(UserIdentifier):
    """Gets a list of the notes assigned to a User Identifier."""
    linked_notes = Note.objects.filter(linked_user=UserIdentifier)
    return linked_notes

def check_user(user_identifier):
    """Check that a user_identifier meets validation requirements."""
    id_to_test = user_identifier.split('-')
    if len(id_to_test) != settings.DICE_ROLLS:
        return False
    # Check that all words in code-phrase are unique
    set_id_to_test = set(id_to_test)
    if len(set_id_to_test) != len(id_to_test):
        return False
    # Grab the word_list from the path specified in settings.py
    wordlist_as_list = get_wordlist()
    # Check that all words are in the dictionary.
    check_all_words = all(item in wordlist_as_list for item in id_to_test)
    if check_all_words == False:
        return False
    else:
        return True
# --------------------DECORATORS AND MIXINS-----------------------------
# Django decorators wrap functions (such as views) in other functions. 
# Mixins perform a similar function for class based views.
# ----------------------------------------------------------------------

def validate_user(view_func):
    """A decorator that calls check_user validator."""
    @functools.wraps(view_func)
    def validate_user_identifier(request, user_identifier, *args, **kwargs):
        get_user_identifier = check_user(user_identifier)
        if get_user_identifier == False:
            return redirect('user-login-error', user_identifier=user_identifier)
        else:
            response = view_func(request, user_identifier, *args, **kwargs)
        return response
    return validate_user_identifier

class PassUserIdentifierMixin:
    """Mixin that passes user_identifier from CBV kwargs to view
    context in a 'results' dictionary, which allows it to be called in template
    with results.user_identifier (same as FBV)."""
    def get_context_data(self, **kwargs):          
        context = super().get_context_data(**kwargs)
        if 'user_identifier' in self.kwargs:
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

# --------------------------SPECIFIC VIEWS------------------------------
# The functions below are listed in the order that a user is likely to 
# encounter them (e.g., generate a codename, then login with codename.)
# ----------------------------------------------------------------------
#
# -------------IDENTIFIER, LOGIN, ACCOUNT REQUEST VIEWS-----------------
# Initial views related to landing, user_identifier, and gitlab account
# requests for users.
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
        linked_notes = get_linked_notes(working_user)
        results['linked_issues'] = linked_issues
        results['linked_notes'] = linked_notes        
    # whether user found or not found, pass 'user_identifier' to context dictionary
    results['user_identifier'] = user_identifier
    return render(request, 'anonticket/user_landing.html', {'results': results})

class UserLoginErrorView(TemplateView):
    """A generic landing page if a username doesn't pass validation tests."""
    template_name = 'anonticket/user_login_error.html'

class GitlabAccountRequestCreateView(
    PassUserIdentifierMixin, CreateView):
    """A view for users to create gitlab account requests."""
    model = GitlabAccountRequest
    fields = [
        'username', 
        'email', 
        'reason',
        ]
    template_name_suffix = '_user_create'

    def form_valid(self, form):
        """Populate user_identifier FK from URL if present, without allowing duplicate
        pending requests."""
        # If user_identifier in the URL path, set variable user_identifier.
        if 'user_identifier' in self.kwargs:
            user_identifier = self.kwargs['user_identifier']
            # make sure it's a valid user_identifier
            if check_user(user_identifier) == False:
                return redirect('user-login-error', user_identifier=user_identifier)
             # Then try to grab the user_identifier from URL from database.
            try: 
                url_user = UserIdentifier.objects.get(user_identifier=user_identifier)
                # if the User Identifier exists, see if has made any account requests
                gl_requests = GitlabAccountRequest.objects.filter(linked_user=url_user)
                if len(gl_requests) != 0:
                    for request in gl_requests:
                        if request.reviewer_status == 'P':
                            return redirect('cannot-create-with-user', user_identifier=user_identifier)
                        # If you get this far, save the form with the new account request.
                        form.instance.linked_user = url_user
                 # if the User Identifier exists, but does not have a pending GL request, make one.
                else:
                    form.instance.linked_user = url_user
            # If the user_identifier doesn't exist, create it and save the request.
            except ObjectDoesNotExist:
                new_user = UserIdentifier(user_identifier=user_identifier)
                new_user.save()
                form.instance.linked_user = new_user
        # Either way, return the valid form.
        return super(GitlabAccountRequestCreateView, self).form_valid(form)
    
    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        working_object = self.object
        if working_object.linked_user:
            working_url = reverse('issue-created', args=[working_object.linked_user])
        else:
            working_url = reverse('created-no-user')
        return working_url

class CannotCreateObjectView(PassUserIdentifierMixin, TemplateView):
    """"""
    template_name = 'anonticket/cannot_create.html'
# -------------------------PROJECT VIEWS----------------------------------
# Views related to creating/looking up issues.
# ----------------------------------------------------------------------

@method_decorator(validate_user, name='dispatch')
class ProjectListView(PassUserIdentifierMixin, ListView):
    """Simple List View of all projects."""
    queryset = Project.objects.order_by('name_with_namespace')

@method_decorator(validate_user, name='dispatch')
class ProjectDetailView(DetailView):
    """A detail view of a single project, which also validates user_identifier
    and fetches the project and issues from gitlab."""
    model = Project

    def get_context_data(self, **kwargs):
        # Grab kwargs          
        context = super().get_context_data(**kwargs)
        # set user_identifier for results dict.
        user_identifier = self.kwargs['user_identifier']
        context['results'] = {'user_identifier': user_identifier}
        # Fetch the working project from the database or 404                    
        project_slug = self.kwargs['slug']
        db_project = Project.objects.get(
            slug=project_slug
        )
        # Get the page_number to paginate the GL API call.
        page_number = self.kwargs['page_number']
        context['page_number'] = page_number
        # Grab the gitlab ID from database and create the project.
        gitlab_id = db_project.gitlab_id
        gl_project = gitlab_get_project(gitlab_id)
        # Save the project attributes to context dict.
        context['gitlab_project'] = gl_project.attributes
        context['open_issues']={}
        check_open = self.get_pagination(
            user_identifier, project_slug, gl_project, page_number, issue_state='opened')
        for key, value in check_open.items():
            context['open_issues'][key] = value
        # grab page of closed issues: note that first page is 1, not 0.
        # closed_issues_list = gl_project.issues.list(
        #     page=page_number, state='closed')
        # context['closed_issues']={}
        # context['closed_issues']['issues_list'] = closed_issues_list
        #determine if there is another page
    
        # check_closed = self.get_pagination(
        #     user_identifier, project_slug, gl_project, page_number, issue_state='closed')
        # for key, value in check_closed.items():
        #     context['closed_issues'][key] = value
        return context

    def get_pagination(
        self, user_identifier, project_slug, gl_project, current_page, issue_state
        ):
        result_dict = {}
        # grab issues list and pass into result_dict (note, 1st page is 1 not 0)
        issues_list = gl_project.issues.list(page=current_page, state=issue_state)
        result_dict['issues'] = issues_list
        # call generator get total_pages and total_issues.
        call_generator = gl_project.issues.list(as_list=False, state=issue_state)
        total_pages = call_generator.total_pages
        total_issues = call_generator.total
        result_dict['total_pages'] = total_pages
        result_dict['total_issues'] = total_issues

        # if current_page > 1, create a "prev" link for button
        if current_page > 1:
            result_dict['prev_url'] = self.make_prev_link(
                current_page, user_identifier, project_slug
            )

        # if total_pages > current_page, create "next" link for button
        if total_pages > current_page:
            result_dict['next_url'] = self.make_next_link(
                current_page, user_identifier, project_slug)
        
        # if total_pages <= 10, render everything.
        if total_pages <= 10:
        # make all prev_links
            result_dict['prev_pages'] = self.make_all_prev_links(
                0, current_page, user_identifier, project_slug)
        # make all post_links
            result_dict['post_pages'] = self.make_all_post_links(
                current_page, total_pages, user_identifier, project_slug)
        # if total pages > 10, then use the current_page to determine how many
        # pages to render before and after.
        elif current_page <= 9:
            # make all prev_links
            result_dict['prev_pages'] = self.make_all_prev_links(
                0, current_page, user_identifier, project_slug)
            # make all post_links UP TO 10
            result_dict['post_pages'] = self.make_all_post_links(
                current_page, 9, user_identifier, project_slug)
            # make a last link
            result_dict['last_page'] = self.make_last_link(
                user_identifier, project_slug, total_pages
            )
        elif (total_pages - current_page) < 5:
            # calculate how many pages will be rendered after current
            post_pages = total_pages - current_page
            # calculate how many links need to be rendered before 
            # the current page
            prev_page_start = current_page - (9 - post_pages)
            # make all prev_links
            result_dict['prev_pages'] = self.make_all_prev_links(
                prev_page_start, current_page, user_identifier, project_slug)
            # make all post_links
            result_dict['post_pages'] = self.make_all_post_links(
                current_page, total_pages, user_identifier, project_slug)
            # make a first link
            result_dict['first_url'] = self.make_first_link(
                user_identifier, project_slug)
        else:
            pass
            # lif (total_pages - current_page) < 5:
            # # calculate how many pages will be rendered after current
            # post_pages = total_pages - current_page
            # # calculate how many links need to be rendered before 
            # # the current page
            # prev_page_start = current_page - (9 - post_pages)
            # # make all prev_links
            # result_dict['prev_pages'] = self.make_all_prev_links(
            #     prev_page_start, current_page, user_identifier, project_slug)
            # # make all post_links
            # result_dict['post_pages'] = self.make_all_post_links(
            #     current_page, total_pages, user_identifier, project_slug)
            # # make a first link
            # result_dict['first_page'] = self.make_first_link(
            #     user_identifier, project_slug)
        return result_dict

    def make_prev_link(self, current_page, user_identifier, project_slug):
        """Creates the 'prev' button link for issue pagination."""
        prev_page = current_page - 1
        prev_url = reverse(
            'project-detail', args=[
                user_identifier, project_slug, prev_page
            ]
        )
        return prev_url   

    def make_next_link(self, current_page, user_identifier, project_slug):
        """Creates the 'next' button link for issue pagination."""
        next_page = current_page + 1
        next_url = reverse(
            'project-detail', args=[
                user_identifier, project_slug, next_page
            ]
        )
        return next_url
    
    def make_first_link(
        self, user_identifier, project_slug):
        """Create links for a "first" page."""
        first_url = reverse(
            'project-detail', args=[
                user_identifier, project_slug, 1
            ]
        )
        return first_url

    def make_last_link(
        self, user_identifier, project_slug, last_page):
        """Create link for a "last" page."""
        results = {}
        last_url = reverse(
            'project-detail', args=[
                user_identifier, project_slug, last_page
            ]
        )
        results['page_number'] = last_page
        results['url'] = last_url
        return results
    
    def make_all_prev_links(self, start_page, current_page, user_identifier, project_slug):
        """Create links and page numbers for pages before current page."""
        results = {}
        starting_page = start_page
        while starting_page < (current_page - 1):
            starting_page += 1
            page_number = starting_page
            page_url = reverse(
                'project-detail', args=[
                    user_identifier, project_slug, page_number
                ]
            )
            results[page_number] = page_url
        return results

    def make_all_post_links(
        self, current_page, end_page, user_identifier, project_slug):
        """Create links and page numbers for pages after current page."""
        results = {}
        starting_page = current_page
        while starting_page < end_page:
            starting_page += 1
            page_number = starting_page
            page_url = reverse(
                'project-detail', args=[
                    user_identifier, project_slug, page_number
                ]
            )
            results[page_number] = page_url
        return results


   
# -------------------------ISSUE VIEWS----------------------------------
# Views related to creating/looking up issues.
# ----------------------------------------------------------------------

@validate_user
def create_issue_view(request, user_identifier, *args):
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

class ObjectCreatedNoUserView(TemplateView):
    """View that tells the user their issue was successfully created. Use
    when creation request was anonymous."""
    template_name = 'anonticket/create_issue_success.html'

@method_decorator(validate_user, name='dispatch')
class PendingIssueDetailView(PassUserIdentifierMixin, DetailView):
    """View for pending issues that have not been mod approved."""
    model = Issue
    template_name = 'anonticket/issue_pending.html'

@validate_user
def issue_detail_view(request, user_identifier, project_slug, gitlab_iid):
    """Detailed view of an issue that has been approved and posted to GL."""
    results = {}
    #Fetch project from database via slug in URL - if cannot be fetched,
    # return a 404 error.
    database_project = get_object_or_404(Project, slug=project_slug)
    results['user_identifier']=user_identifier
    # Use the gitlab_id from database project to fetch project from gitlab.
    # (Increases security.)
    gitlab_id = database_project.gitlab_id
    working_project = gitlab_get_project(project=gitlab_id)
    results['project'] = working_project.attributes
    go_back_url = reverse('project-detail', args=[user_identifier, project_slug])
    results['go_back_url'] = go_back_url
    working_issue = gitlab_get_issue(project=gitlab_id, issue=gitlab_iid)
    results['issue'] = working_issue.attributes
    # Get the notes list, and then for every note in the list, grab that
    # note's attributes, which includes the body text, etc.
    results['notes'] = []
    notes_list = gitlab_get_notes_list(project=gitlab_id, issue=gitlab_iid)
    for note in notes_list:
        note_dict = note.attributes
        results['notes'].append(note_dict)
    results['notes'].reverse()
    # Generate notes link.
    new_note_link = reverse('create-note', args=[
        user_identifier, project_slug, gitlab_iid
        ])
    results['new_note_link'] = new_note_link
    return render(request, 'anonticket/issue_detail.html', {'results': results})

@validate_user
def issue_search_view(request, user_identifier):
    """Allows a user to select a project and search Gitlab for issues matching
    a search string."""
    results = {}
    if 'search_terms' in request.GET:
        form = Anonymous_Ticket_Project_Search_Form(request.GET)
        if form.is_valid():
            results = form.call_project_and_issue(user_identifier)
            results['user_identifier'] = user_identifier
    else:
        form = Anonymous_Ticket_Project_Search_Form
        results['user_identifier'] = user_identifier
    return render(request, 'anonticket/issue_search.html', {'form': form, 'results': results})

# ---------------------------NOTE_VIEWS---------------------------------
# Views related to creating/looking up notes.
# ----------------------------------------------------------------------

@method_decorator(validate_user, name='dispatch')
class NoteCreateView(PassUserIdentifierMixin, CreateView):
    """View to create a note given a user_identifier."""
    model=Note
    fields = ['body']
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        """Populate default Issue object attributes from URL path."""
        linked_project = get_object_or_404(Project, slug=self.kwargs['project'])
        form.instance.linked_project = linked_project
        try:
            linked_user = UserIdentifier.objects.get(user_identifier=self.kwargs['user_identifier'])
            form.instance.linked_user = linked_user
            # If lookup fails, create the user.
        except: 
            new_user = UserIdentifier(user_identifier=self.kwargs['user_identifier'])
            new_user.save()
            form.instance.linked_user = new_user
        issue_iid = self.kwargs['issue_iid']
        form.instance.issue_iid = issue_iid
        return super(NoteCreateView, self).form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        working_object = self.object
        user_identifier_to_pass = working_object.linked_user.user_identifier
        working_url = reverse('issue-created', args=[user_identifier_to_pass])
        return working_url

class PendingNoteDetailView(PassUserIdentifierMixin, DetailView):
    """View For Pending Notes that have not been  mod approved."""
    model = Note
    template_name = 'anonticket/note_pending.html'
    
# ----------------------MODERATOR_VIEWS---------------------------------
# Views related to moderators. Should all have decorator 
# @staff_member_required, which forces staff status and allows access
# to the login form from the admin panel, and the @is_moderator 
# decorator, which tests that user is a member of the group Moderator.
# ----------------------------------------------------------------------

#Functions that check group status:

def is_moderator(user):
    """Check if the user is either in the Moderators group or a superuser."""
    if user.groups.filter(name="Moderators").exists() == True:
        return True
    elif user.is_superuser:
        return True
    else:
        return False

def is_account_approver(user):
    """Check if the user is in the Account Approvers group or superuser."""
    if user.groups.filter(name="Account Approvers").exists() == True:
        return True
    elif user.is_superuser:
        return True
    else:
        return False

def is_mod_or_approver(user):
    """A function to check that a logged-in user is either a moderator,
    an account approver, or a super_user."""
    if is_moderator(user) == True:
        return True
    elif is_account_approver(user) == True:
        return True
    else:
        return False

# Set the login_redirect_url variable. Staff should not be able to
# access NoteUpdateView or IssueUpdateView without going through
# /moderator first, so all moderator views can redirect to the 
# same place in the event the staff member is not logged in.
 
login_redirect_url = "/tor_admin/login/?next=/moderator/"

@user_passes_test(
    is_mod_or_approver, login_url=login_redirect_url)
@staff_member_required
def moderator_view(request):
    """View that allows moderators and account approvers to approve pending items."""
    from anonticket.forms import (
        PendingNoteFormSet, 
        PendingIssueFormSet, 
        PendingGitlabAccountRequestFormSet,
        )
    user = request.user
    messages = {}
    if request.method == 'POST':
        # if POST, verify that the user is in the moderators group.
        if is_moderator(user) == True:
            note_formset = PendingNoteFormSet(
                prefix="note_formset", data=request.POST)
            issue_formset = PendingIssueFormSet(
                prefix="issue_formset", data=request.POST)
            if issue_formset.is_valid():
                issue_formset.save()
            if note_formset.is_valid():
                note_formset.save()
            else:
                print(issue_formset.errors)
                print(note_formset.errors)
        # or that the user is in the account approvers group.
        if is_account_approver(user) == True:
            gitlab_formset = PendingGitlabAccountRequestFormSet(
                prefix="gitlab_formset", data=request.POST)
            if gitlab_formset.is_valid():
                gitlab_formset.save()
            else:
                print(gitlab_formset.errors)
        # Regardless of result, return redirect to 'moderator' 
        return redirect('/moderator/')
    else:
        # if request method is not POST, pull formsets and render them in the template.
        if is_moderator(user) == True:
            note_formset = PendingNoteFormSet(prefix="note_formset")
            issue_formset = PendingIssueFormSet(prefix="issue_formset")
        else:
            note_formset = {}
            issue_formset = {}
            messages['note_message'] = """You do not have permission to 
            view pending notes at this time."""
            messages['issue_message'] = """You do not have permission to 
            view pending issues at this time."""
        if is_account_approver(user) == True:
            gitlab_formset = PendingGitlabAccountRequestFormSet(
                prefix="gitlab_formset")
        else:
            gitlab_formset = {}
            messages['gitlab_message'] = """You do not 
            have permission to view pending Gitlab account requests at this time."""
    return render(request, "anonticket/moderator.html", {
        "note_formset": note_formset, 
        "issue_formset":issue_formset,
        "gitlab_formset": gitlab_formset, 
        "messages": messages
        })

@method_decorator(user_passes_test(
    is_moderator, login_url=login_redirect_url), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ModeratorNoteUpdateView(UpdateView):
    """View that allows a moderator to update a Note."""
    model = Note
    fields= ['body', 'mod_comment', 'reviewer_status']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        url = reverse('moderator')
        return url

@method_decorator(user_passes_test(
    is_moderator, login_url=login_redirect_url), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ModeratorIssueUpdateView(UpdateView):
    """View that allows a moderator to update an issue."""
    model = Issue
    fields= ['linked_project', 'description', 'mod_comment', 'reviewer_status']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        url = reverse('moderator')
        return url

@method_decorator(user_passes_test(
    is_account_approver, login_url=login_redirect_url), name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class ModeratorGitlabAccountRequestUpdateView(UpdateView):
    """View that allows a moderator to update an issue."""
    model = GitlabAccountRequest
    fields= ['username', 'email', 'reason', 'mod_comment','reviewer_status']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        url = reverse('moderator')
        return url