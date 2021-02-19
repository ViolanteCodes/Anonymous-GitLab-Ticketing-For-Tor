"""Tests specific to Gitlab bot and Gitlab Fail Gracefully"""

from django.conf import settings
from django.test import SimpleTestCase, Client, tag, override_settings
from test_plus.test import TestCase, CBVTestCase
from django.urls import reverse, resolve
from django.core.cache import cache
from anonticket.models import Project, Issue, Note
from anonticket.views import ProjectDetailView
# Import gitlab and relevant gl_bot functions.
import gitlab
from gl_bot.gitlabdown import (
    GitlabDownObject, GitlabDownProject, GitlabDownIssue, GitlabDownNote)
from requests.exceptions import ConnectTimeout, ConnectionError

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
