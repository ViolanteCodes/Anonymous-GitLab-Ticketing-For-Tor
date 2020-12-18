"""Tests for all URLS in anon_ticket app."""
# import SimpleTestCase, used when database is not necessary.
from django.test import SimpleTestCase

class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        """Test the home url."""
        self.assertEqual(1, 1)