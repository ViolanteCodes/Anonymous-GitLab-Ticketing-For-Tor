import requests
import urllib
import socket
import gitlab

# import urllib3
# from urllib3.exceptions import ConnectionError, TimeoutError
from requests.exceptions import ConnectTimeout 

class GitlabDownObject:
    """A mocked version of the Gitlab Object for when Gitlab is down."""
    def __init__(self):
        self.projects = GitlabDownProject()

class GitlabDownProject:
    """A mocked version of the Gitlab Object for when Gitlab is down."""
    def __init__(self):
        self.name = 'Gitlab Timed Out'
        self.attributes = {
            'created_at': '2020-12-01T17:19:24.061Z',
            'description': 'A mock project that displays when GitLab calls time out.',
            'id': 'NA',
            'last_activity_at': '2020-12-15T21:45:42.934Z',
            'name': 'GitLab Timed Out',
            'name_with_namespace': 'The Tor Project / Anon-Ticket',
            'namespace': {   'avatar_url': None,
                            'full_path': 'tpo/tpa',
                            'id': 480,
                            'kind': 'group',
                            'name': 'TPA',
                            'parent_id': 268,
                            'path': 'tpa',
                            'web_url': 'https://gitlab.torproject.org/groups/tpo/tpa'},
            'tag_list': [],
            'web_url': 'https://gitlab.torproject.org/tpo/tpa/anon-ticket',
        }
        self.issues = GitlabDownIssue()

    def get(self, id):
        return self

    def __strt__(self):
        return self.name

class GitlabDownIssue:
    """A mocked version of a GitLab issue for when GitLab is down."""
    def __init__(self):
        self.title = """OH NO! IF YOU'RE SEEING THIS, SOMETHING WENT WRONG! This 
        is a dummy issue generated when the call to the Gitlab API times out.
        The most likely culprit is that GitLab is currently down, which means we 
        can't communicate with the API. Please try again later!"""
        self.iid = 99999
        self.attributes = {
            'assignee': {
                'name': '',
                'state': '',
                'username': '',
                'web_url': ''},
            'assignees': [   {   'avatar_url': None,
                                    'id': 748,
                                    'name': 'MariaV',
                                    'state': 'active',
                                    'username': 'MariaV',
                                    'web_url': ''}],
            'author': {   'avatar_url': None,
                            'id': 748,
                            'name': '',
                            'state': 'active',
                            'username': '',
                            'web_url': 'https://gitlab.torproject.org/MariaV'},
            'confidential': False,
            'created_at': '',
            'description': """***This issue is generated when the call to the GitLab API times out.
                The most likely culprit is that either GitLab or its API is currently down. 
                Please try again later!***""",
            'due_date': None,
            'id': '',
            'iid': '',
            'labels': [],
            'milestone': {  'created_at': '',
                            'description': 'A fake milestone',
                            'title': 'GITLAB TIMED OUT',
                            'updated_at': '',
                            'web_url': ''},
            'project_id': '',
            'state': 'opened',
            'title': """OH NO! IF YOU'RE SEEING THIS, SOMETHING WENT WRONG!""",
            'updated_at': '',
            'web_url': '',
            }
        self.notes = GitlabDownNote()

    def get(self, id):
        """A mocked version of the .get method, which just returns self."""
        return self

    def list(self, as_list=True, state='opened', **kwargs):
        """A mocked version of the .list() method from a GitLab Project object. Returns
        issue attributes inside of a list if as_list is true, returns a mocked issue
        generator if false."""

        if as_list == True:
            if state=='opened':
                issues_list = []
                issues_list.append(self)
                return issues_list
            else:
                blank_list =[]
                return blank_list
        else:
            if state=='opened':
                instantiate_generator = self.GitlabDownIssueGenerator(total=1)
                return instantiate_generator
            else:
                instantiate_generator = self.GitlabDownIssueGenerator(total=0)
                return instantiate_generator

    def __str__(self):
        return self.title

    class GitlabDownIssueGenerator:
        """A mocked version of the Issue Generator Object in Gitlab."""
        def __init__(self, total):
            self.total_pages = total
            self.total = total

class GitlabDownNote:
    """A mocked version of a GitLab note for when GitLab is down."""
    def __init__(self):
        self.name = 'GitLab API call failed.'
        self.attributes = {
            'body': """***If you're seeing this note, it means that the call 
                to the gitlab API timed out.***""",
            'created_at': '',
            'id': 9999999,
            'issue_iid': 9999999,
            'noteable_id': 310028,
            'noteable_iid': 1,
            'noteable_type': 'Issue',
            'project_id': 740,
            'updated_at': ''
        }
    
    def list(self, **kwargs):
        """A mocked version of the issue.notes.list() method."""
        notes_list = []
        notes_list.append(self)
        return notes_list

gl_real = gitlab.Gitlab('https://abjklejsoiejs.org', private_token='yP1V1PyY7baf6AjxeKJ8', timeout=1)
gl_fake = GitlabDownObject()

def get_project():
    try:
        project = gl_real.projects.get(1)
    except ConnectTimeout:
        project = gl_fake.projects.get(1)
    return project

project = get_project()
print(project.attributes)
issue = project.issues.get(1)
print(issue)
issues_list = project.issues.list()
print(issues_list)
notes = issue.notes.list()
print(notes)
