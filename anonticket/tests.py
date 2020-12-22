from django.conf import settings
from anonticket.models import UserIdentifier, Project, Issue
from django.views.generic import TemplateView, DetailView
from anonticket.views import *
from django.urls import reverse, resolve
from django.test import SimpleTestCase, Client
from test_plus.test import TestCase, CBVTestCase


# Create your tests here.

# ---------------------------URL TESTS----------------------------------
# URL Tests using Django SimpleTestCase (no need for database.)
# ----------------------------------------------------------------------

class TestUrls(SimpleTestCase):
    """Test that the URLS in the anonticket resolve."""

    def test_home_url_is_resolved(self):
        """Test the 'home' URL."""
        url = reverse('home')
        self.assertEqual(resolve(url).func.view_class, TemplateView)
  
    def test_create_identifier_url_is_resolved(self):
        """Test the 'create-identifier' URL."""
        url = reverse('create-identifier')
        self.assertEqual(resolve(url).func.view_class, CreateIdentifierView)

    def test_login_url_is_resolved(self):
        """Test the 'login' URL."""
        url = reverse('login')
        self.assertEqual(resolve(url).func, login_view)

    def test_user_login_error_url_is_resolved(self):
        """Test the 'user-login-error URL."""
        url = reverse('user-login-error', args=["bad-identifier"])
        self.assertEqual(resolve(url).func.view_class, UserLoginErrorView)

    def test_issue_created_url_is_resolved(self):
        """Test the 'issue-created' URL."""
        url = reverse('issue-created', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.assertEqual(resolve(url).func.view_class, IssueSuccessView)

    def test_create_issue_url_is_resolved(self):
        """Test the 'create-issue' URL."""
        url = reverse('create-issue', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.assertEqual(resolve(url).func, create_issue_view)

    def test_issue_detail_view_is_resolved(self):
        """Test the 'issue-detail-view' URL."""
        url = reverse('issue-detail-view', args=[
            'duo-atlas-hypnotism-curry-creatable-rubble',
            740, 1])
        self.assertEqual(resolve(url).func, issue_detail_view)

    def test_pending_issue_detail_view_is_resolved(self):
        """Test the 'pending-issue-detail-view' URL."""
        url = reverse('pending-issue-detail-view', args = [
            'duo-atlas-hypnotism-curry-creatable-rubble',
            747, 
            13])
        self.assertEqual(resolve(url).func.view_class, PendingIssueDetailView)
        
    def test_user_landing_url_is_resolved(self):
        """Test the 'user-landing' URL."""
        url = reverse('user-landing', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.assertEqual(resolve(url).func, user_landing_view)

# --------------------------VIEW TESTS----------------------------------
# Tests for views: status = 200, template correct.
# ----------------------------------------------------------------------

class TestViews(TestCase):
    """Test the functions in views.py"""

    def setUp(self):
        """Set up a project, user identifier, and issue in the test database."""

        self.client = Client()
        self.home_url = reverse('home')
        self.create_identifier_url = reverse('create-identifier')
        self.login_url = reverse('login')
        self.user_landing_url = reverse('user-landing', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.user_login_error_url = reverse('user-login-error', args=["bad-identifier"])
        self.create_issue_url = reverse('create-issue', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.issue_success_url =  reverse('issue-created', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.pending_issue_url =  reverse('pending-issue-detail-view', args = ['duo-atlas-hypnotism-curry-creatable-rubble', 740, 1])
        self.issue_detail_url = reverse('issue-detail-view', args=[ 'duo-atlas-hypnotism-curry-creatable-rubble', 740, 2])

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

        UserIdentifier.objects.create(
            user_identifier = 'antonym-roundup-ravishing-leggings-chooser-oversight'
        )

        UserIdentifier.objects.create(
            user_identifier = 'duo-atlas-hypnotism-curry-creatable-rubble'
        )

        Issue.objects.create (
            issue_title = 'A pending issue',
            issue_description = 'A pending issue description',
            linked_project = Project.objects.get(project_name='anon-ticket'),
            linked_user = UserIdentifier.objects.get(user_identifier='duo-atlas-hypnotism-curry-creatable-rubble'),
            id = 1
        )

        Issue.objects.create (
            issue_title = 'A posted issue',
            issue_description = 'A posted issue description',
            linked_project = Project.objects.get(project_name='anon-ticket'),
            linked_user = UserIdentifier.objects.get(user_identifier='duo-atlas-hypnotism-curry-creatable-rubble'),
            issue_iid = 1,
            reviewer_status = 'A',
            posted_to_GitLab = True
        )
    
    def test_home_view_GET(self):
        """Test the response for home_view"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/index.html')

    def test_create_identifier_view_GET(self):
        """Test the response for create_identifier_view"""
        response = self.client.get(self.create_identifier_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/create_identifier.html')
    
    def test_login_view_GET(self):
        """Test the response for login_view"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/user_login.html')

    def test_user_landing_view_GET(self):
        """Test the response for user_landing_view"""
        response = self.client.get(self.user_landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/user_landing.html')

    def test_user_login_error_view_GET(self):
        """Test the response for user_login_error view"""
        response = self.client.get(self.user_login_error_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/user_login_error.html')

    def test_create_issue_GET(self):
        """Test the response for create_issue view"""
        response = self.client.get(self.create_issue_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/create_new_issue.html')

    def test_issue_success_view_GET(self):
        """Test the response for IssueSuccessView"""
        response = self.client.get(self.issue_success_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/create_issue_success.html')
    
    def test_pending_issue_detail_view_GET(self):
        """Test the response for PendingIssueDetailView"""
        response = self.client.get(self.pending_issue_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/issue_pending.html')

    def test_issue_detail_view_GET(self):
        """Test the response for issue_detail_view"""
        response = self.client.get(self.issue_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/issue_detail.html')

    def test_get_wordlist(self):
        """Test get_wordlist function."""
        word_list_path = settings.WORD_LIST_PATH
        with open(word_list_path) as f:
            known_wordlist = f.read().splitlines()
        test_wordlist = get_wordlist()
        self.assertEqual(known_wordlist, test_wordlist)

    # def test_validate_user_identifier(self):
    #     """Test validate_user_identifier function."""
    #     seven_words = 'test-test-test-test-test-test-test'
    #     test_seven_words = validate_user_identifier(seven_words)
    #     self.assertEqual(test_seven_words, False)
    #     word_not_in_dict = 'antonym-roundup-ravishing-leggings-chooser-asdfasdf'
    #     test_word_not_in_dict = validate_user_identifier(word_not_in_dict)
    #     self.assertEqual(test_word_not_in_dict, False)
    #     known_good_identifier = 'antonym-roundup-ravishing-leggings-chooser-oversight'
    #     test_known_good_identifier = validate_user_identifier(known_good_identifier)
    #     self.assertEqual(test_known_good_identifier, True)

    def test_user_identifier_in_database(self):
        """Test user_identifier_in_database function"""
        known_good_user = 'antonym-roundup-ravishing-leggings-chooser-oversight'
        test_known_good_user = user_identifier_in_database(known_good_user)
        self.assertEqual(test_known_good_user, True)
        known_bad_user = 'test-test-test-test-test-test'
        test_known_bad_user = user_identifier_in_database(known_bad_user)
        self.assertEqual(test_known_bad_user, False)

    def test_generate_user_identifier_list(self):
        """Test the generate_user_identifier_list function from CreateIdentifierView."""
        word_list = get_wordlist()
        list_to_test = CreateIdentifierView.generate_user_identifier_list(self)
        for word in list_to_test:
            self.assertIn(word, word_list)
    
    def test_context_dict(self):
        """Tests the context_dict function from CreateIdentifierView."""
        words_to_test = [
            'word1',
            'word2',
            'word3',
            'word4',
            'word5',
            'word6',
        ]
        test_context = CreateIdentifierView.context_dict(self, word_list = words_to_test)
        known_context = {
            'chosen_words': words_to_test,            
            'user_identifier_string': 'word1-word2-word3-word4-word5-word6',
        }
        self.assertEqual(test_context, known_context)

    def test_get_context_data(self):
        """Tests the get_context_data function from CreateIdentifierView by verifying the 
        returned results is a dictionary with key['chosen_words'], value = list of 
        settings.DICE_ROLLS words, with all words from wordlist, and key['user_identifier_string'],
        the value of which contains all chosen words. Also asserts that key['user_found'] is 
        not returned (unique user.)"""
        word_list_path = settings.WORD_LIST_PATH
        with open(word_list_path) as f:
            known_wordlist = f.read().splitlines()
        test_create_identifier_view = CreateIdentifierView()
        test_get_context = test_create_identifier_view.get_context_data()
        self.assertTrue(len(test_get_context['chosen_words']) == settings.DICE_ROLLS)
        for word in test_get_context['chosen_words']:
            self.assertIn(word, known_wordlist)
            self.assertIn(word, test_get_context['user_identifier_string'])
        self.assertNotIn('user_found', test_get_context.keys())

class TestFilters(TestCase):
    """Test custom filters."""
    
    def test_pretty_datetime(self):
        """Test the pretty_datetime filter."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-10-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 February, 2020 - 14:09 UTC')