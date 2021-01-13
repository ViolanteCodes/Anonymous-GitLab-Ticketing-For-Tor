from django.conf import settings
from django.test import SimpleTestCase, Client, tag
from test_plus.test import TestCase, CBVTestCase
from django.urls import reverse, resolve
from anonticket.models import UserIdentifier, Project, Issue
from django.views.generic import TemplateView, DetailView
from anonticket.views import *
from anonticket.forms import (
    LoginForm, 
    Anonymous_Ticket_Base_Search_Form,
    Anonymous_Ticket_Project_Search_Form, 
    CreateIssueForm)

# Create your tests here.

# Note: If you run tests with --tag prefix, you can test a small suite
# of tests with one of the tags below (registered with '@tag'.)
#   Examples:
#   $ python manage.py test --tag url 
#   (or with coverage) $ coverage run manage.py --tag url.)

# ---------------------------URL TESTS----------------------------------
# URL Tests using Django SimpleTestCase (no need for database.)
# ----------------------------------------------------------------------

@tag('url')
class TestUrls(SimpleTestCase):
    """Test that the URLS in the anonticket resolve."""
    def setUp(self):
        self.new_user = 'duo-atlas-hypnotism-curry-creatable-rubble'
        self.project_slug = 'a-project-slug'

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

    def test_create_note_url_is_resolved(self):
        """Test the 'create-note' URL."""
        url = reverse('create-note', args=[
            self.new_user, self.project_slug, 1
        ])
        self.assertEqual(resolve(url).func.view_class, NoteCreateView)

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

    def test_issue_search_url_is_resolved(self):
        """Test the 'issue-search' URL."""
        url = reverse('issue-search', args = [
            self.new_user
        ])
        self.assertEqual(resolve(url).func, issue_search_view)

    def test_project_detail_view_url_is_resolved(self):
        """Test the 'project-detail' URL."""
        url = reverse('project-detail', args= [
            self.new_user, self.project_slug
        ])
        self.assertEqual(resolve(url).func.view_class, ProjectDetailView)

    def test_project_list_is_resolved(self):
        """Test the 'project-list' URL."""
        url = reverse('project-list', args=[
            self.new_user
        ])
        self.assertEqual(resolve(url).func.view_class, ProjectListView)

    def test_issue_created_url_is_resolved(self):
        """Test the 'issue-created' URL."""
        url = reverse('issue-created', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.assertEqual(resolve(url).func.view_class, IssueSuccessView)

    def test_create_issue_url_is_resolved(self):
        """Test the 'create-issue' URL."""
        url = reverse('create-issue', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.assertEqual(resolve(url).func, create_issue_view)
        
    def test_user_landing_url_is_resolved(self):
        """Test the 'user-landing' URL."""
        url = reverse('user-landing', args=['duo-atlas-hypnotism-curry-creatable-rubble'])
        self.assertEqual(resolve(url).func, user_landing_view)

# --------------------------VIEW TESTS----------------------------------
# Tests for views: (generally for status = 200, template correct,
# although some POST views also test for redirects, etc.
# ----------------------------------------------------------------------

@tag('id_no_db')
class TestIdentifierAndLoginViewsWithoutDatabase(SimpleTestCase):
    """Test the functions in views.py under the Identifier and Login
    views section that do not require database."""

    def setUp(self):
        # Create a user
        self.new_user = 'duo-atlas-hypnotism-curry-creatable-rubble'
        self.client = Client()
        self.home_url = reverse('home')
        self.create_identifier_url = reverse('create-identifier')
        self.login_url = reverse('login')
        self.user_landing_url = reverse('user-landing', args=[self.new_user])
        self.user_login_error_url = reverse('user-login-error', args=["bad-identifier"])

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

    def test_login_view_GET_with_data(self):
        """Test the response for the login_view with data."""
        response = self.client.get(self.login_url, data={
            'word_1': 'duo',
            'word_2': 'atlas',
            'word_3': 'hypnotism',
            'word_4': 'curry',
            'word_5': 'creatable',
            'word_6': 'rubble',
        })
        self.assertEqual(response.status_code, 302)

    def test_user_landing_view_GET(self):
        """Test the response for user_landing_view with known good user_identifier."""
        response = self.client.get(self.user_landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/user_landing.html')

    def test_user_landing_view_GET_seven_words(self):
        """Test the user_landing_view with a known bad identifier 
        (seven words) and verify decorator redirect"""
        too_many_words_url = reverse(
            'user-landing', args=[
                'duo-atlas-hypnotism-curry-creatable-rubble-brunch'])
        response = self. client.get(too_many_words_url)
        self.assertEqual(response.status_code, 302)
    
    def test_user_landing_view_GET_bad_word(self):
        """Test the user_landing_view with a known bad identifier 
        (wrong word) and verify decorator redirect"""
        too_many_words_url = reverse(
            'user-landing', args=[
                'duo-atlas-hypnotism-curry-creatable-moxie'])
        response = self. client.get(too_many_words_url)
        self.assertEqual(response.status_code, 302)

    def test_user_landing_view_GET_repeated_word(self):
        """Test the user_landing_view with a known bad identifier 
        (repeated word) and verify decorator redirect"""
        repeated_words_url = reverse(
            'user-landing', args=[
                'duo-atlas-hypnotism-curry-creatable-creatable'])
        response = self.client.get(repeated_words_url)
        self.assertEqual(response.status_code, 302)

    def test_user_login_error_view_GET(self):
        """Test the response for user_login_error view"""
        response = self.client.get(self.user_login_error_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/user_login_error.html')

@tag('id_with_db')
class TestIdentifierAndLoginViewsWithDatabase(TestCase):
    """ Test the functions in views.py under the Identifier and Login
    views section that require database."""

    def setUp(self):
        """Set up a project, user identifier, and issue in the test database."""
        # Setup project
        new_project = Project(gitlab_id=747)
        # Should fetch gitlab details on save.
        new_project.save()
        # Create a user
        new_user = UserIdentifier.objects.create(
            user_identifier = 'duo-atlas-hypnotism-curry-creatable-rubble'
        )
        # Create a pending issue.
        pending_issue = Issue.objects.create (
            title = 'A Pending Issue',
            linked_project = new_project,
            linked_user = new_user,
            description= 'A description of a pending issue'
        )
        # Create a posted issue.
        posted_issue = Issue.objects.create (  
            title = 'A posted issue',
            description = 'A posted issue description',
            linked_project = new_project,
            linked_user = new_user,
            gitlab_iid = 1,
            reviewer_status = 'A',
            posted_to_GitLab = True
        )
        self.client=Client()
        self.user_landing_url = reverse('user-landing', args=[new_user])

    def test_user_landing_view_GET_with_data(self):
        """Test the response for user_landing_view with known good user_identifier."""
        response = self.client.get(self.user_landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/user_landing.html')

@tag('project')
class TestProjectViews(TestCase):
    """Test the project functions in views.py"""

    def setUp(self):
        """Set up a project, user identifier, and issue in the test database."""
        # Setup project
        new_project = Project(gitlab_id=747)
        # Should fetch gitlab details on save.
        new_project.save()
        # Create a user
        new_user = UserIdentifier.objects.create(
            user_identifier = 'duo-atlas-hypnotism-curry-creatable-rubble'
        )
        self.client=Client()
        self.project_list_view_url = reverse('project-list', args=[new_user])
        self.project_detail_view_url = reverse('project-detail', args=[
            new_user, new_project.slug])
        self.new_user = new_user
    
    def test_project_list_GET(self):
        """Test the response for the ProjectListView"""
        response = self.client.get(self.project_list_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/project_list.html')

    def test_project_detail_GET(self):
        """Test the response for the ProjectDetailView"""
        response = self.client.get(self.project_detail_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/project_detail.html')

@tag('issues')
class TestIssuesViews(TestCase):
    """Test the issues functions in views.py"""

    def setUp(self):
        """Set up a project, user identifier, and issue in the test database."""
        # Setup project
        new_project = Project(gitlab_id=747)
        # Should fetch gitlab details on save.
        new_project.save()
        # Create a user
        new_user = UserIdentifier.objects.create(
            user_identifier = 'duo-atlas-hypnotism-curry-creatable-rubble'
        )
        # Create a pending issue.
        pending_issue = Issue.objects.create (
            title = 'A Pending Issue',
            linked_project = new_project,
            linked_user = new_user,
            description= 'A description of a pending issue'
        )
        # Create a posted issue.
        posted_issue = Issue.objects.create (  
            title = 'A posted issue',
            description = 'A posted issue description',
            linked_project = new_project,
            linked_user = new_user,
            gitlab_iid = 1,
            reviewer_status = 'A',
            posted_to_GitLab = True
        )
        self.client=Client()
        self.create_issue_url = reverse('create-issue', args=[new_user])
        self.issue_success_url =  reverse('issue-created', args=[new_user])
        self.pending_issue_url =  reverse('pending-issue-detail-view', args = [
            new_user, new_project.slug, pending_issue.pk])
        self.issue_detail_url = reverse('issue-detail-view', args=[
            new_user, new_project.slug, posted_issue.gitlab_iid])
        self.issue_search_url = reverse('issue-search', args=[new_user])
        self.new_user = new_user
        self.project = new_project

    def test_create_issue_GET(self):
        """Test the response for create_issue view"""
        response = self.client.get(self.create_issue_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/create_new_issue.html')

    def test_create_issue_POST_current_user(self):
        """Test the response for create_issue view with a current user."""
        form_data = {
            'linked_project': self.project.pk,
            'title':'A new descriptive issue title',
            'description': 'Yet another description of the issue.'
        }
        form=CreateIssueForm(form_data)
        expected_url = reverse('issue-created', args=[self.new_user])
        response = self.client.post(self.create_issue_url, form=form, data=form_data, follow=False)
        self.assertRedirects(response, expected_url)

    def test_create_issue_POST_new_user(self):
        """Test the response for create_issue view with a new user."""
        create_url = reverse('create-issue', args=[
            'autopilot-stunt-unfasten-dirtiness-wipe-blissful'
        ])
        form_data = {
            'linked_project': self.project.pk,
            'title':'A new descriptive issue title',
            'description': 'Yet another description of the issue.'
        }
        form=CreateIssueForm(form_data)
        expected_url = reverse('issue-created', args=[
            'autopilot-stunt-unfasten-dirtiness-wipe-blissful'])
        response = self.client.post(create_url, form=form, data=form_data, follow=False)
        self.assertRedirects(response, expected_url)

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

    def test_issue_search_view_GET_valid_data(self):
        """Test the reponse for the issue_search_view"""
        url = reverse('issue-search', args=[self.new_user])
        form_data = {
            'choose_project': self.project.pk,
            'search_terms': 'issue'
        }
        response = self.client.get(url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/issue_search.html')

    def test_issue_search_view_GET_invalid_data(self):
        """Test the response for the issue_search_view with no search_terms."""
        url = reverse('issue-search', args=[self.new_user])
        form_data = {
            'choose_project': self.project.pk,
        }
        response = self.client.get(url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/issue_search.html')

    def test_issue_search_view_GET_no_matches(self):
        """Test the reponse for the issue_search_view"""
        url = reverse('issue-search', args=[self.new_user])
        form_data = {
            'choose_project': self.project.pk,
            'search_terms': 'i-dont-match-anything'
        }
        response = self.client.get(url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'anonticket/issue_search.html')  

@tag('notes')
class TestNotesViews(TestCase):
    """Test the notes functions in views.py."""

    def setUp(self):
        """Set up a project, user identifier, and issue in the test database."""
        # Setup project
        new_project = Project(gitlab_id=747)
        # Should fetch gitlab details on save.
        new_project.save()
        # Create a user
        new_user = UserIdentifier.objects.create(
            user_identifier = 'duo-atlas-hypnotism-curry-creatable-rubble'
        )
        # Create a pending issue.
        pending_issue = Issue.objects.create (
            title = 'A Pending Issue',
            linked_project = new_project,
            linked_user = new_user,
            description= 'A description of a pending issue'
        )
        # Create a posted issue.
        posted_issue = Issue.objects.create (  
            title = 'A posted issue',
            description = 'A posted issue description',
            linked_project = new_project,
            linked_user = new_user,
            gitlab_iid = 1,
            reviewer_status = 'A',
            posted_to_GitLab = True
        )
        self.client=Client()
        self.new_user = new_user
        self.project = new_project
        self.issue = posted_issue

    def test_note_create_view_POST_existing_user(self):
        """Test the note create view with valid data, with a 
        user that already exists."""
        url = reverse('create-note', args=[
            self.new_user, self.project.slug, self.issue.gitlab_iid])
        form_data = {
            'body': """A new note body."""
        }
        expected_url = reverse('issue-created', args=[self.new_user])
        response = self.client.post(url, form_data)
        self.assertRedirects(response, expected_url)

    def test_note_create_view_POST_new_user(self):
        """Test the note create view with valid_data, with a
        user that doesn't get exist."""
        new_user = 'autopilot-stunt-unfasten-dirtiness-wipe-blissful'
        url = reverse('create-note', args=[
            new_user, self.project.slug, self.issue.gitlab_iid])
        form_data = {
            'body': """A new note body."""
        }
        expected_url = reverse('issue-created', args=[new_user])
        response = self.client.post(url, form_data)
        self.assertRedirects(response, expected_url)

@tag('other_with_db')
class TestViewsOtherWithDatabase(TestCase):
    """Test the functions in views.py not directly related to one of the above
    that require a database."""

    def setUp(self):
        """Set up a project, user identifier, and issue in the test database."""
        new_user = UserIdentifier.objects.create(
            user_identifier = 'duo-atlas-hypnotism-curry-creatable-rubble'
        )
        self.new_user = new_user

    def test_user_identifier_in_database(self):
        """Test user_identifier_in_database function"""
        test_known_good_user = user_identifier_in_database(self.new_user.user_identifier)
        self.assertEqual(test_known_good_user, True)
        known_bad_user = 'test-test-test-test-test-test'
        test_known_bad_user = user_identifier_in_database(known_bad_user)
        self.assertEqual(test_known_bad_user, False)

@tag('other_no_db')
class TestViewsOtherWithoutDatabase(SimpleTestCase):
    """Test the functions in views.py not directly related to one of the above
    that do NOT require a database (simpletestcase)."""
    
    def test_get_wordlist(self):
        """Test get_wordlist function."""
        word_list_path = settings.WORD_LIST_PATH
        with open(word_list_path) as f:
            known_wordlist = f.read().splitlines()
        test_wordlist = get_wordlist()
        self.assertEqual(known_wordlist, test_wordlist)

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

# --------------------------FORM TESTS----------------------------------
# Tests for forms.py: basic tests to see that form_is_valid(). Testing
# for integration with views, etc., is done in views.py above.
# ----------------------------------------------------------------------

@tag('login')
class TestLoginForm(SimpleTestCase):
    """Test the Login Form from forms.py."""

    def test_login_valid_data(self):
        """Test login form with valid data."""
        # duo-atlas-hypnotism-curry-creatable-rubble
        form = LoginForm(data = {
            'word_1': 'duo',
            'word_2': 'atlas',
            'word_3': 'hypnotism',
            'word_4': 'curry',
            'word_5': 'creatable',
            'word_6': 'rubble',
        })
        self.assertTrue(form.is_valid())
    
    def test_login_invalid_data(self):
        """Test login form with invalid data."""
        # duo-atlas-hypnotism-curry-creatable-rubble
        form = LoginForm(data = {
            'word_1': 'duo',
            'word_2': 'atlas',
            'word_3': 'hypnotism',
            'word_4': 'curry',
            'word_5': 'creatable',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

@tag('search_form')
class TestAnonymousTicketProjectSearchForm(TestCase):
    """Test the Anonymous_Ticket_Project_Search_Form"""

    def setUp(self):
        # Setup project
        new_project = Project(gitlab_id=747)
        # Should fetch gitlab details on save.
        new_project.save()
        self.project = new_project

    def test_project_search_form_valid_data(self):
        """Test the Project Search Form with valid data."""
        form=Anonymous_Ticket_Project_Search_Form(data={
            'choose_project':self.project,
            'search_terms':'issue'
        })
        self.assertTrue(form.is_valid())

    def test_project_search_form_invalid_data(self):
        """Test the Project Search Form with valid data."""
        form=Anonymous_Ticket_Project_Search_Form(data={
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

@tag('create_issue_form')
class TestCreateIssueForm(TestCase):
    """Test the CreateIssueForm"""

    def setUp(self):
        # Setup project
        new_project = Project(gitlab_id=747)
        # Should fetch gitlab details on save.
        new_project.save()
        self.project = new_project
        new_user = UserIdentifier.objects.create(
            user_identifier = 'duo-atlas-hypnotism-curry-creatable-rubble'
        )
        self.new_user = new_user
        self.create_issue_url = reverse('create-issue', args=[new_user])
        client=Client()

    def test_create_issue_form_valid_data(self):
        """Test the Project Search Form with valid data."""
        form_data = {
            'linked_project': self.project,
            'title':'A descriptive issue title',
            'description': 'A description of the issue.'
        }
        form=CreateIssueForm(form_data)
        self.assertTrue(form.is_valid())

    def test_create_issue_form_invalid_data(self):
        """Test the Project Search Form with valid data."""
        form=CreateIssueForm(data={
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 3)

# --------------------------OTHER TESTS---------------------------------
# Tests for filters, custom template tags, etc.
# ----------------------------------------------------------------------

@tag('filters')
class TestFilters(SimpleTestCase):
    """Test custom filters."""
    
    def test_pretty_datetime_january(self):
        """Test the pretty_datetime filter for january."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-01-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 January, 2020 - 14:09 UTC')

    def test_pretty_datetime_february(self):
        """Test the pretty_datetime filter for february."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-02-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 February, 2020 - 14:09 UTC')
    
    def test_pretty_datetime_march(self):
        """Test the pretty_datetime filter for march."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-03-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 March, 2020 - 14:09 UTC')

    def test_pretty_datetime_april(self):
        """Test the pretty_datetime filter for april."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-04-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 April, 2020 - 14:09 UTC')

    def test_pretty_datetime_may(self):
        """Test the pretty_datetime filter for may."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-05-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 May, 2020 - 14:09 UTC')

    def test_pretty_datetime_june(self):
        """Test the pretty_datetime filter for june."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-06-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 June, 2020 - 14:09 UTC')

    def test_pretty_datetime_july(self):
        """Test the pretty_datetime filter for july."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-07-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 July, 2020 - 14:09 UTC')

    def test_pretty_datetime_august(self):
        """Test the pretty_datetime filter for march."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-08-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 August, 2020 - 14:09 UTC')

    def test_pretty_datetime_september(self):
        """Test the pretty_datetime filter for september."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-09-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 September, 2020 - 14:09 UTC')
    
    def test_pretty_datetime_october(self):
        """Test the pretty_datetime filter for october."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-10-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 October, 2020 - 14:09 UTC')

    def test_pretty_datetime_november(self):
        """Test the pretty_datetime filter for november."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-11-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 November, 2020 - 14:09 UTC')
    
    def test_pretty_datetime_december(self):
        """Test the pretty_datetime filter for december."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-12-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 December, 2020 - 14:09 UTC')

    def test_pretty_datetime_undefined_month(self):
        """Test the pretty_datetime filter for a bad month."""
        from shared.templatetags.custom_filters import pretty_datetime
        iso_test_string = "2020-13-19T14:09:46.500Z"
        pretty_iso_string = pretty_datetime(iso_test_string)
        self.assertEqual(pretty_iso_string, '19 undefined, 2020 - 14:09 UTC')