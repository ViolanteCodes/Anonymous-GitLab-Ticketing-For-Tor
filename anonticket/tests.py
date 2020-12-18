from test_plus.test import TestCase
from anonticket.models import UserIdentifier, Project, Issue
from anonticket.views import *   
from django.conf import settings

# Create your tests here.

class TestViews(TestCase):
    """Test the functions in views.py"""

    def setUp(self):
        """Set up a project, user identifier, and issue in the test database."""
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

    def test_get_wordlist(self):
        """Test get_wordlist function."""
        word_list_path = settings.WORD_LIST_PATH
        with open(word_list_path) as f:
            known_wordlist = f.read().splitlines()
        test_wordlist = get_wordlist()
        self.assertEqual(known_wordlist, test_wordlist)

    def test_validate_user_identifier(self):
        """Test validate_user_identifier function."""
        seven_words = 'test-test-test-test-test-test-test'
        test_seven_words = validate_user_identifier(seven_words)
        self.assertEqual(test_seven_words, False)
        word_not_in_dict = 'antonym-roundup-ravishing-leggings-chooser-asdfasdf'
        test_word_not_in_dict = validate_user_identifier(word_not_in_dict)
        self.assertEqual(test_word_not_in_dict, False)
        known_good_identifier = 'antonym-roundup-ravishing-leggings-chooser-oversight'
        test_known_good_identifier = validate_user_identifier(known_good_identifier)
        self.assertEqual(test_known_good_identifier, True)

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

    # def test_project_attributes(self):
    #     """Test that the attributes in test_project validate correctly."""
    #     test_project = Project.objects.get(pk=1)
    #     self.assertEqual(test_project.project_name, "anon-ticket")
    #     self.assertEqual(test_project.project_description, "Anonymous ticket handling front-end for Gitlab.")
    #     self.assertEqual(test_project.project_slug, "anon-ticket")
    #     self.assertEqual(test_project.project_id, 740)

    # def test_project_search_known_bad(self):
    #     """Test project_search method with known bad choose_project (GitLab 
    #     integration error test.)"""
    #     TestFormProjectBad = Anonymous_Ticket_Project_Search_Form
    #     self.cleaned_data = {}
    #     self.cleaned_data['choose_project'] = "a-bad-project"
    #     test_result = TestFormProjectBad.project_search(self)
    #     self.assertEqual(test_result, {
    #         'project_status': 'failed', 
    #         'project_message': 'This project could not be fetched from gitlab.\n'
    #          "It likely does not exist, or you don't have access to it."
    #         })
    
    # def test_project_search_known_good(self):
    #     """Test project_search method with known good choose_project (GitLab 
    #     integration test.)"""
    #     TestFormProjectGood = Anonymous_Ticket_Project_Search_Form
    #     self.cleaned_data = {}
    #     self.cleaned_data['choose_project'] = "anon-ticket"
    #     test_result = TestFormProjectGood.project_search(self)
    #     self.assertEqual(test_result, {
    #         'project_status': 'Project found, pending issue.', 
    #         'project_name': 'anon-ticket', 
    #         'project_description': 'Anonymous ticket handling front-end for Gitlab.'
    #         })
    
    # def test_issue_search_known_good(self):
    #     """Test issue_search with known good choose_project and issue_iid (GitLab 
    #     integration test.)"""
    #     TestFormIssueGood = Anonymous_Ticket_Project_Search_Form
    #     self.cleaned_data = {}
    #     self.cleaned_data['choose_project'] = "anon-ticket"
    #     self.cleaned_data['issue_iid'] = "1"
    #     project_id = 740
    #     issue_iid = 1
    #     project_result = {
    #         'project_status':'Project found, pending issue.', 
    #         'project_name': 'anon-ticket', 
    #         'project_description': 'Anonymous ticket handling front-end for Gitlab.',
    #         }
    #     self.linked_project = gl.projects.get(project_id)
    #     issue_test = TestFormIssueGood.issue_search(self, project_result=project_result)

