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
        elif self.cleaned_data['project_id']:
            project_id = self.cleaned_data['choose_project']
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
        return result

    def issue_search(self, project_result={}):
        """Pass the data from the issue_iid CharField to github and 
        look up the project details."""
        result = project_result
        result['issue_status'] = 'pending'
        if result['project_status'] != 'failed':
            issue_iid = self.cleaned_data['issue_iid']
            try:
                issue = self.linked_project.issues.get(issue_iid)
            except gitlab.exceptions.GitlabGetError:
                result['status'] = 'failed'
                result['message'] = issue_not_found_message
            # If issue lookup was successful, add issue details and notes to
            # results dictionary.
            if result['status'] != 'failed':
                result['id']=issue.id 
                result['title']=issue.title
                result['description']=issue.description
                notes_text = []
                notes_list = issue.notes.list()
                for note in notes_list:
                    working_text = note.body
                    formatted_note_text = working_text.split("\n")
                    notes_text.extend(formatted_note_text)
                result['notes_text']=notes_text
                result['status'] = 'Success'
                result['message'] = 'Your ticket has been found.'
        return result

    def call_project_and_issue(self):
        """Call the project_search and issue_search methods and send the
        relevant information to GitLab to look up a ticket."""
        project_result = self.project_search()
        result = self.issue_search(project_result=project_result)
        return result

class Anonymous_Ticket_Project_Search_Form(Anonymous_Ticket_Base_Search_Form):
    """A form to let users search for an issue with a given project 
    and issue_id."""
    
    choose_project = forms.ModelChoiceField(queryset=Project.objects.all())
    issue_iid = forms.IntegerField(max_value = 9223372036854775807)

class Create_Anonymous_Issue_Form(Anonymous_Ticket_Base_Search_Form):
    """A form to let users add an issue to a given project in gitlab."""
    choose_project = forms.ModelChoiceField(queryset=Project.objects.all())
    issue_title = forms.CharField(max_length=200)
    description_of_issue = forms.CharField(widget=forms.Textarea)

    def create_issue(self):
        """Create an issue for a project in GitLab."""
        # Search for the project using the project_search method from base class.
        result=self.project_search()
        # if project was found, assign issue text and title and try to post
        if result['status'] != 'failed':
            cleaned_issue_title = self.cleaned_data['issue_title']
            cleaned_description_of_issue = self.cleaned_data['description_of_issue']
            try:
                issue = self.linked_project.issues.create({
                    'title':cleaned_issue_title,
                    'description': cleaned_description_of_issue,
                })
            except gitlab.exceptions.GitlabCreateError:
                result['status'] = 'failed'
                result['message'] = issue_not_created_message
            # If issue lookup was successful, add issue details and notes to
            # results dictionary.
            if result['status'] != 'failed':
                result['issue_title']=issue.title 
                result['description']=issue.description
                result['status'] = 'Success'
                result['message'] = 'Your issue has been created.'
        return result

class Save_Anonymous_Ticket(ModelForm):
    """A form to let users request a GitLab issue be added for review."""

    class Meta:
        model = Issue
        fields = ['linked_project', 'issue_title', 'issue_description']


