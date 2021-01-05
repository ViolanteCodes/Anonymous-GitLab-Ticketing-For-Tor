from django import forms
from django.forms import ModelForm
from django.conf import settings
import gitlab
import random
from .models import Project, Issue, UserIdentifier

gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_SECRET_TOKEN)

# Messages to be shared across forms go here.

project_not_found_message = """This project could not be fetched from gitlab.
It likely does not exist, or you don't have access to it."""
issue_not_found_message = """Your project was found, but this issue 
could not be fetched from gitlab. It likely does not exist, or you
don't have access to it."""
unknown_error_message = """This lookup failed for a reason not currently
accounted for by our current error handling."""
successful_issue_lookup_message = """Your project and issue were both 
found and fetched from gitlab. Project and issue details, including
associated notes, are listed below."""
issue_not_created_message = """Unable to create this issue."""

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

class Anonymous_Ticket_Base_Search_Form(forms.Form):
    """Contains the methods common to all forms when searching for tickets 
    by project, id, etc."""

    def project_search(self):
        """Pass the data from the project_id to github and look up the 
        project details."""
        # Check if you are receiving data from a form field for
        # project_id.
        if self.cleaned_data['choose_project']:
            choose_project = self.cleaned_data['choose_project']
            working_project = Project.objects.get(project_name=choose_project)
            project_id = working_project.project_id
        result = {}
        # Set result['passed'] with a pending flag to capture events.
        result['project_status'] = 'pending'
        # try to fetch project from gitlab
        # Call project_search method for form.
        try: 
            linked_project = gl.projects.get(project_id)
        # if project does not exist (python-gitlab raises GitlabGetError)
        # pass failed status and failure message into result dictionary.
        except gitlab.exceptions.GitlabGetError:
            result['project_status'] = 'failed'
            result['project_message'] = project_not_found_message
        except:
            result['project_message'] = unknown_error_message
            result['project_status'] = 'failed'
        # If successful on project lookup, pass project information into
        # dictionary and try to fetch issue from gitlab.
        if result['project_status'] != 'failed':    
            self.linked_project = linked_project
            result['status'] = """Project found, pending issue."""
            result['project_name'] = self.linked_project.name
            result['project_description'] = self.linked_project.description
            result['project_id'] = linked_project.id
        return result

    def issue_search(self, project_result={}):
        """Pass the data from the search_term CharField to github and 
        look up the project details."""
        result = project_result
        if result['project_status'] != 'failed':
            search_string = self.cleaned_data['search_terms']
            try:
                search_issues = self.linked_project.search('issues', search_string)
            except gitlab.exceptions.GitlabGetError:
                result['status'] = 'failed'
                result['message'] = issue_not_found_message
            except:
                result['status'] = 'failed'
                results['message'] = unknown_error_message
            # If issue lookup was successful, add issue details and notes to
            # results dictionary.
            if result['status'] != 'failed':
                result['matching_issues'] = search_issues
                if result['matching_issues']:
                    result['status'] = 'success'
                    result['message'] = 'Here are issues matching your search string:'
                else:
                    result['status'] = 'no matches'
                    result['message'] = """Your search executed successfully,
                    but no issues matching this search string were found."""
        return result

    def call_project_and_issue(self):
        """Call the project_search and issue_search methods and send the
        relevant information to GitLab to look up a ticket."""
        project_result = self.project_search()
        result = self.issue_search(project_result=project_result)
        return result

class Anonymous_Ticket_Project_Search_Form(Anonymous_Ticket_Base_Search_Form):
    """A form to let users search for an issue or notes matching a project string."""
    
    choose_project = forms.ModelChoiceField(queryset=Project.objects.all())
    search_terms = forms.CharField(max_length=200)

class CreateIssueForm(ModelForm):
    class Meta:
        model = Issue
        fields = ('linked_project', 'issue_title', 'issue_description')
        labels = {
            'linked_project': ('Linked Project'),
            'issue_title': ('Title of Your Issue'),
            'issue_description': ('Describe Your Issue'),
        }
        help_texts = {
            'linked_project': ("""Choose the project associated with this issue.
            If you do not see your project in the drop-down, it isn't using
            this anonymous issue handling system."""),
            'issue_title': ("""Give your issue a descriptive title."""),
            'issue_description': ("""Describe the issue you are reporting. 
            Please be as specific as possible about the circumstances that
            provoked the issue and the behavior that was noticed."""),
        }






