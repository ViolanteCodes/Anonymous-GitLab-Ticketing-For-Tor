"""Tests specific to Gitlab bot and Gitlab Fail Gracefully"""

from django.conf import settings
from django.test import SimpleTestCase, Client, tag, override_settings
from test_plus.test import TestCase, CBVTestCase
from django.urls import reverse, resolve
from django.core.cache import cache
from anonticket.models import Project, Issue, Note, UserIdentifier
from anonticket.views import ProjectDetailView
# Import necessary functions from views
from anonticket.views import gitlab_get_project
# Import gitlab and relevant gl_bot functions.
import gitlab
from gl_bot.gitlabdown import (
    GitlabDownObject, GitlabDownProject, GitlabDownIssue, GitlabDownNote)
from requests.exceptions import ConnectTimeout, ConnectionError
from unittest.mock import patch

# import get functions from view

# Note: If you run tests with --tag prefix, you can test a small suite
# of tests with one of the tags below (registered with '@tag'.)
#   Examples:
#   $ python manage.py test --tag url 
#   (or with coverage) $ coverage run manage.py --tag url.)

# ---------------------GITLAB BOT ATTRIBUTES----------------------------
# Basic tests for API calls with GitlabBot
# ----------------------------------------------------------------------

@tag('gitlab-bot-basic')
class TestGitLabBotBasic(SimpleTestCase):
    """Direct testing of GitLabDownObject and related objects, including 
    making calls for issues, notes, etc."""
    def setUp(self):
        """Instantiate the object."""
        gl = GitlabDownObject()
        self.gl = gl
        self.project_id = 9999
        self.issue_id = 9999
    
    def test_gl_project_get(self):
        """Simulate a project get call."""
        test_project = self.gl.projects.get(self.project_id)
        self.assertEqual(test_project.name, 'Gitlab Timed Out')
        self.assertEqual(test_project.attributes['name'], 'GitLab Timed Out')

    def test_gl_issue_get(self):
        """Simulate an issue get call."""
        test_project = self.gl.projects.get(self.project_id)
        test_issue = test_project.issues.get(self.issue_id)
        self.assertEqual(
            test_issue.title, "OH NO! IF YOU'RE SEEING THIS, SOMETHING WENT WRONG!")
        self.assertEqual(
            test_issue.attributes['description'], 
            """***This message is generated when the call to the GitLab API times out.
                The most likely culprit is that either GitLab or its API is currently down. 
                Please try again later!***""")
    
    def test_gl_issue_list_state_opened(self):
        """Simulate an issue list call with as_list == True and state = 'opened'."""
        test_project = self.gl.projects.get(self.project_id)
        test_issue = test_project.issues.get(self.issue_id)
        test_issue_list = test_project.issues.list(as_list=True, state='opened')
        #Assert that there is a single object in the list.
        self.assertTrue(len(test_issue_list)==1)
        #Assert that the object attributes.['title'] is correct
        for item in test_issue_list:
            self.assertEqual(
                item.attributes['title'], 
                "OH NO! IF YOU'RE SEEING THIS, SOMETHING WENT WRONG!")

    def test_gl_issue_list_generator_state_opened(self):
        """Simulate an issue list call with as_list == False (generator) with state = 'opened."""
        test_project = self.gl.projects.get(self.project_id)
        test_issue = test_project.issues.get(self.issue_id)
        test_issue_list = test_project.issues.list(as_list=False, state='opened')
        # Check that the object that wsa returned is a generator with
        # a total_pages and a total attribute.
        self.assertEqual(test_issue_list.total_pages, 1)
        self.assertEqual(test_issue_list.total, 1)

    def test_gl_issue_list_state_closed(self):
        """Simulate an issue list call with as_list=True and state='closed'."""
        test_project = self.gl.projects.get(self.project_id)
        test_issue = test_project.issues.get(self.issue_id)
        test_issue_list = test_project.issues.list(as_list=True, state='closed')
        # Assert the list came back empty
        self.assertTrue(len(test_issue_list)==0)

    def test_gl_issue_list_generator_state_closed(self):
        """Simulate an issue list call with as_list=False and state='closed."""
        test_project = self.gl.projects.get(self.project_id)
        test_issue = test_project.issues.get(self.issue_id)
        test_issue_list = test_project.issues.list(as_list=False, state='closed')
        # Check that the object that wsa returned is a generator with
        # a total_pages and a total attribute.
        self.assertEqual(test_issue_list.total_pages, 0)
        self.assertEqual(test_issue_list.total, 0)

    def test_gl_issues_notes(self):
        """Simulate the issue.note() call."""
        test_project = self.gl.projects.get(self.project_id)
        test_issue = test_project.issues.get(self.issue_id)
        test_notes = test_issue.notes
        self.assertEqual(test_notes.name, 'GitLab API call failed.')

    def test_gl_issue_notes_list(self):
        """Simulate the issue.notes.list() call."""
        test_project = self.gl.projects.get(self.project_id)
        test_issue = test_project.issues.get(self.issue_id)
        test_notes_list = test_issue.notes.list()
        self.assertEqual(len(test_notes_list), 1)
        for note in test_notes_list:
            self.assertEqual(note.name, "GitLab API call failed.")
            self.assertEqual(note.attributes['id'],9999999)

@tag('gitlab-bot-views')
class TestGitlabBotProjectViewGet(TestCase):
    """Test that GitLabDown Object is called when data is mocked"""

    def setUp(self):
        """Set Up Test"""
        tor_project = Project(gitlab_id=426)
        tor_project.save()
        self.tor_project = tor_project
        gl_project = gitlab_get_project(426, public=True)
        self.gl_project = gl_project
        new_user = UserIdentifier.objects.create(
            user_identifier = 'duo-atlas-hypnotism-curry-creatable-rubble'
        )
        self.client = Client()
        self.new_user = new_user
        self.project_detail_view_url = reverse('project-detail', args=[
            self.new_user, self.tor_project.slug, 1])
        self.issue_detail_view_url = reverse('issue-detail-view-go-back', args=[
            self.new_user, self.tor_project.slug, 1, 1])

    @patch("django.conf.settings.GITLAB_URL", settings.TIMEOUT_URL)
    def test_project_detail_view_GET_patched(self):
        """Test the project detail view with patched gitlab URL."""
        response = self.get(self.project_detail_view_url)
        self.response_200()
        # Assert object in context is tor object from database.
        self.assertInContext('object')
        self.assertEqual(self.context['object'], self.tor_project)
        # Assert total pages and total issues = 1 (Test Generator)
        self.assertEqual(self.context['open_issues']['total_pages'], 1)
        self.assertEqual(self.context['open_issues']['total_issues'], 1)
        # Assert context dict is built correctly
        self.assertInContext('page_number')
        self.assertEqual(self.context['page_number'], 1)
        self.assertInContext('gitlab_project')
        # Assert the project in context dict is the gitlab Project
        self.assertEqual(
            self.context['gitlab_project']['description'],
            "A mock project that displays when GitLab calls time out."
            )
        # Assert the open issues dict has one object inside of it, and that
        # It is the mock issue.
        issue_object_key = self.context['open_issues']['issues'].keys()
        self.assertEqual(len(self.context['open_issues']['issues'].keys()), 1)
        for item in issue_object_key:
            self.assertEqual(item.title, "OH NO! IF YOU'RE SEEING THIS, SOMETHING WENT WRONG!")
        
    @patch("django.conf.settings.GITLAB_URL", settings.TIMEOUT_URL)
    def test_issue_detail_view_go_back_GET_patched(self):
        """Test the issue detail view with patched gitlab URL."""
        response = self.get(self.issue_detail_view_url)
        self.response_200()
        # Assert project has been passed as 'project' to context dict.
        # Assert object in context is tor object from database.
        self.assertInContext('results')
        # Assert glbot project object in results dict
        self.assertEqual(
            self.context['results']['project']['description'],
            "A mock project that displays when GitLab calls time out.")
        # Assert glbot issue object in results dict
        self.assertEqual(
            self.context['results']['issue']['title'],
            "OH NO! IF YOU'RE SEEING THIS, SOMETHING WENT WRONG!")
        # Assert that a notes list was returned, that it has a single
        # note in it, and that the note body starts with the correct
        # string.
        self.assertEqual(
            len(self.context['results']['notes']), 1)
        notes_list = self.context['results']['notes']
        for note in notes_list:
            self.assertIn("""***If you're seeing this note""", note['body'])  


