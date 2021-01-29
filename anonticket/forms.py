from django import forms
from django.forms import ModelForm, modelformset_factory, BaseModelFormSet
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
import gitlab
import random
from .models import UserIdentifier, Project, Issue, Note, GitlabAccountRequest

# Initialize GitLab Object
gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_SECRET_TOKEN)

class LoginForm(forms.Form):
    """A form that allows users to enter in their keycodes to login."""
    word_1 = forms.CharField(max_length=9)
    word_2 = forms.CharField(max_length=9)
    word_3 = forms.CharField(max_length=9)
    word_4 = forms.CharField(max_length=9)
    word_5 = forms.CharField(max_length=9)
    word_6 = forms.CharField(max_length=9)

    def join_words(self):
        """Pull cleaned data from form and join into code_phrase"""
        word_list = []
        word_list.append(self.cleaned_data['word_1'])
        word_list.append(self.cleaned_data['word_2'])
        word_list.append(self.cleaned_data['word_3'])
        word_list.append(self.cleaned_data['word_4'])
        word_list.append(self.cleaned_data['word_5'])
        word_list.append(self.cleaned_data['word_6'])
        join_key = '-'
        code_phrase = join_key.join(word_list)
        return code_phrase

# Forms relating to User Objects:

class Anonymous_Ticket_Base_Search_Form(forms.Form):
    """A base search form with all the methods necessary to search for
    projects, issues, and tickets."""

    def project_search(self):
        """Pass the data from the gitlab_id to github and look up the 
        project details."""
        # Setup a results dictionary
        result = {}
        # Setup messages dictionary for project.
        messages = {
            'gitlab_project_not_found_message': """This project could not be 
            fetched from gitlab. It likely does not exist, or you don't 
            have access to it.""",
            'unknown_project_error_message': """This lookup failed for 
            a reason not currently accounted for by our current error 
            handling.""",
        }
        result['project_status'] = 'pending'
        if self.cleaned_data['choose_project']:
            working_project = self.cleaned_data['choose_project']
        # Try to grab project matching form selection out of database.
        try: 
            working_project = get_object_or_404(
                Project, name_with_namespace=working_project)
            self.database_project = working_project
        # Once Project is found, grab project info from gitlab.
            try:
                id_to_grab = working_project.gitlab_id 
                linked_project = gl.projects.get(id_to_grab)
            # if project does not exist (python-gitlab raises GitlabGetError)
            # pass failed status and failure message into result dictionary.
            except gitlab.exceptions.GitlabGetError:
                result['project_status'] = 'failed'
                result['project_message'] = messages['gitlab_project_not_found_message']
            except:
                result['project_message'] = messages['unknown_project_error_message']
                result['project_status'] = 'failed'
        except Project.DoesNotExist:
            raise Http404("No Project matches the given query.")
        except:
            pass
        # If successful on project lookup, add project as attribute to
        # form Object and save project in dictionary as 'matching_project'.
        if result['project_status'] != 'failed':    
            self.linked_project = linked_project
            result['status'] = 'pending'
            result['matching_project'] = linked_project
        return result

    def issue_search(self, project_result={}):
        """Pass the data from the search_term CharField to github and 
        look up the project details."""
        result = project_result
        messages = {
            'could_not_fetch_issue_message': """Your project was found, but 
            this issue could not be fetched from gitlab. It likely does 
            not exist, or you don't have access to it.""",
            'successful_issue_lookup_message': """Issues matching this search string 
            are displayed in the table below.""",
            'no_matching_issues_message': """Your search executed successfully,
            but no issues matching this search string were found.""",
            'unknown_issue_error_message': """This lookup failed for
            unknown reasons."""
        }
        if result['status'] == 'pending':
            search_string = self.cleaned_data['search_terms']
            result['search_string'] = search_string
            try:
                search_issues = self.linked_project.search('issues', search_string)
                result['matching_issues'] = search_issues
                if result['matching_issues']:
                    result['status'] = 'success'
                    result['message'] = messages['successful_issue_lookup_message']
                else:
                    result['status'] = 'no matches'
                    result['message'] = messages['no_matching_issues_message']
            except gitlab.exceptions.GitlabGetError:
                result['status'] = 'failed'
                result['message'] = messages['could_not_fetch_issue_message']
            except:
                result['status'] = 'failed'
                result['message'] = messages['unknown_issue_error_message']                
        return result

    def get_issue_links(self, issue_result={}, user_identifier='user_identifier'):
        """Formulate a link to the issue detail page for each issue in the 
        list"""
        result = issue_result
        if result['status'] == 'success':
            for issue in result['matching_issues']:
                issue['detail_url'] = reverse(
                    'issue-detail-view', args=[
                        user_identifier, self.database_project.slug, issue['iid'],
                    ])
        return result

    def call_project_and_issue(self, user_identifier):
        """Call the project_search and issue_search methods and send the
        relevant information to GitLab to look up a ticket."""
        project_result = self.project_search()
        issue_result = self.issue_search(project_result=project_result)
        with_issue_links = self.get_issue_links(
            issue_result=issue_result, user_identifier=user_identifier)
        return with_issue_links

class Anonymous_Ticket_Project_Search_Form(Anonymous_Ticket_Base_Search_Form):
    """A form to let users search for an issue or notes matching a project string."""
    choose_project = forms.ModelChoiceField(
        queryset=Project.objects.all(), 
        label="Choose a project.",
        help_text="Not all Tor projects can be searched via this portal."
        )
    search_terms = forms.CharField(
        max_length=200,
        label="Enter a short search string.",
        help_text="""Shorter strings are better, as this search will find
        exact matches only."""
        )

class CreateIssueForm(ModelForm):
    class Meta:
        model = Issue
        fields = ('linked_project', 'title', 'description')
        labels = {
            'linked_project': ('Linked Project'),
            'title': ('Title of Your Issue'),
            'description': ('Describe Your Issue'),
        }
        help_texts = {
            'linked_project': ("""Choose the project associated with this issue."""),
            'title': ("""Give your issue a descriptive title."""),
            'description': ("""Describe the issue you are reporting. 
            Please be as specific as possible about the circumstances that
            provoked the issue and the behavior that was noticed. You 
            can use <a href='https://docs.gitlab.com/ee/user/markdown.html'
            target="_blank">
            GitLab Flavored Markdown (GFM)</a> on this form.""")
        }

# The following forms and formsets are used to created the 'moderator' view

class PendingIssueForm(forms.ModelForm):
    """A special version of the Issue Form to be used with PendingIssueFormset."""
    class Meta:
        model = Issue
        fields = (
            'reviewer_status',)
    
    def __init__(self, *args, **kwargs):
       super(PendingIssueForm, self).__init__(*args, **kwargs)
    #    self.fields['linked_project'].disabled = True
    #    self.fields['title'].disabled = True
    #    self.fields['description'].disabled = True

class BasePendingIssueFormSet(BaseModelFormSet):
    """Subclass of Base Formset that sets issue queryset."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset=Issue.objects.filter(reviewer_status='P')

class PendingNoteForm(forms.ModelForm):
    """A special version of the Note Form to be used with PendingNoteFormSet."""
    class Meta:
        model = Note
        fields = (
            'reviewer_status',)
    
    def __init__(self, *args, **kwargs):
       super(PendingNoteForm, self).__init__(*args, **kwargs)
    # Don't actually need this right now, but leave this for later.
    #    self.fields['linked_project'].disabled = True

class BasePendingNoteFormSet(BaseModelFormSet):
    """Subclass of Base Formset that sets queryset."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset=Note.objects.filter(reviewer_status='P')

class PendingGitlabAccountRequestForm(forms.ModelForm):
    """A special version of the Note Form to be used with PendingNoteFormSet."""
    class Meta:
        model = GitlabAccountRequest
        fields = (
            'reviewer_status',)

    def __init__(self, *args, **kwargs):
       super(PendingGitlabAccountRequestForm, self).__init__(*args, **kwargs)

class BasePendingGitlabAccountRequestFormset(BaseModelFormSet):
    """Subclass of Base Formset that sets queryset."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset=GitlabAccountRequest.objects.filter(reviewer_status='P')

# Formset Variables to be fed to Pending Admin View.
PendingNoteFormSet = modelformset_factory(
    Note, 
    form=PendingNoteForm, 
    formset=BasePendingNoteFormSet,
    extra=0)

PendingIssueFormSet = modelformset_factory(
    Issue,
    form=PendingIssueForm,
    formset=BasePendingIssueFormSet, 
    extra=0)

PendingGitlabAccountRequestFormSet = modelformset_factory(
    GitlabAccountRequest,
    form=PendingGitlabAccountRequestForm,
    formset=BasePendingGitlabAccountRequestFormset, 
    extra=0)




