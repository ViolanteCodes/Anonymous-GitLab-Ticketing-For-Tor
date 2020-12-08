from test_plus.test import TestCase
from django import forms
from anonticket.forms import (Anonymous_Ticket_Project_Search_Form,
project_not_found_message, issue_not_found_message, unknown_error_message,
successful_issue_lookup_message, gl)
from anonticket.models import Project
    

# Create your tests here.

class AnonymousTicketFormTest(TestCase):
    """Test the functions of the Anonymous_Ticket_Project_Search_Form"""

    def setUp(self):
        """Set up a project in the test database."""
        Project.objects.create(
            project_name="anon-ticket", 
            project_description="Anonymous ticket handling front-end for Gitlab.",
            project_slug="anon-ticket",
            project_id= 740,
        )

        Project.objects.create(
            project_name="a-bad-project", 
            project_description="A known bad test project.",
            project_slug="known-bad",
            project_id= 1,
        )

    def test_project_attributes(self):
        """Test that the attributes in test_project validate correctly."""
        test_project = Project.objects.get(pk=1)
        self.assertEqual(test_project.project_name, "anon-ticket")
        self.assertEqual(test_project.project_description, "Anonymous ticket handling front-end for Gitlab.")
        self.assertEqual(test_project.project_slug, "anon-ticket")
        self.assertEqual(test_project.project_id, 740)

    def test_project_search_known_bad(self):
        """Test project_search method with known bad choose_project (GitLab 
        integration error test.)"""
        TestFormProjectBad = Anonymous_Ticket_Project_Search_Form
        self.cleaned_data = {}
        self.cleaned_data['choose_project'] = "a-bad-project"
        test_result = TestFormProjectBad.project_search(self)
        self.assertEqual(test_result, {
            'project_status': 'failed', 
            'project_message': 'This project could not be fetched from gitlab.\n'
             "It likely does not exist, or you don't have access to it."
            })
    
    def test_project_search_known_good(self):
        """Test project_search method with known good choose_project (GitLab 
        integration test.)"""
        TestFormProjectGood = Anonymous_Ticket_Project_Search_Form
        self.cleaned_data = {}
        self.cleaned_data['choose_project'] = "anon-ticket"
        test_result = TestFormProjectGood.project_search(self)
        self.assertEqual(test_result, {
            'project_status': 'pending', 
            'project_name': 'anon-ticket', 
            'project_description': 'Anonymous ticket handling front-end for Gitlab.'
            })
    
    def test_issue_search_known_good(self):
        """Test issue_search with known good choose_project and issue_iid (GitLab 
        integration test.)"""
        TestFormIssueGood = Anonymous_Ticket_Project_Search_Form
        self.cleaned_data = {}
        self.cleaned_data['choose_project'] = "anon-ticket"
        self.cleaned_data['issue_iid'] = "1"
        project_id = 740
        issue_iid = 1
        project_result = {
            'project_status':'pending', 
            'project_name': 'anon-ticket', 
            'project_description': 'Anonymous ticket handling front-end for Gitlab.',
            }
        self.linked_project = gl.projects.get(project_id)
        issue_test = TestFormIssueGood.issue_search(self, project_result=project_result)

