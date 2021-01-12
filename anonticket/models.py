from django.db import models
from django.conf import settings
from django.utils.text import slugify
import gitlab

# Create your models here.

class UserIdentifier(models.Model):
    """Representation of a user identifier."""
    user_identifier = models.CharField(max_length=200)

    def __str__(self):
        return self.user_identifier

class GitLabGroup(models.Model):
    """Representation of a Gitlab Group in the database. This does not
    need to be supplied by the admin; it will automatically be created if
    a project is put into the database."""
    name = models.CharField(max_length=200, null=True, blank=True, help_text=
    """IMPORTANT: GLGROUPS are AUTOMATICALLY CREATED when a project requiring
    the group has been added--so you shouldn't have to do anything here!""")
    gitlab_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    """Representation of a project in the database. To add a GL project 
    to the database, only the gitlab id number needs to be supplied in the
    gitlab_id field. Upon saving, the project details and any necessary
    group details will be fetched from gitlab."""
    gitlab_id = models.IntegerField(help_text="""IMPORTANT: Enter a 
    gitlab ID into this field and save, and the project's details will 
    be fetched from gitlab! NOTHING ELSE ON THIS FORM NEEDS TO BE 
    FILLED IN. Additionally, if a project is saved, a fresh copy of
    the gitlab details will be fetched and the database entries will
    be updated.""")
    name = models.CharField(max_length=200, null=True, blank=True)
    name_with_namespace = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=50, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    gitlab_group = models.ForeignKey(GitLabGroup, on_delete=models.CASCADE, null=True, blank=True)

    def fetch_from_gitlab(self):
        """Given the gitlab_id, fetch the relevant information from Gitlab."""
        # Create the gitlab object
        gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_SECRET_TOKEN)
        # Grab the associated project from gitlab.
        try: 
            working_project = gl.projects.get(self.gitlab_id)
            self.name = working_project.name
            self.name_with_namespace = working_project.name_with_namespace
            self.description = working_project.description 
            self.slug = slugify(working_project.name)
            self.url = working_project.web_url
        # if the project does not have a gitlab_group foreignkey, first
        # check to see if a GitLabGroup object with the gitlab id exists.
            if not self.gitlab_group:
                gitlab_group_id = working_project.namespace['id']
                try:
                    fetch_group = GitLabGroup.objects.get(gitlab_id=gitlab_group_id)
                    self.gitlab_group = fetch_group
        # if a matching GitLabGroup cannot be fetched, pull the group info from
        # gitlab and create one.
                except:
                    from_gitlab = gl.groups.get(gitlab_group_id)
                    new_group = GitLabGroup.objects.create(
                        name=from_gitlab.name,
                        gitlab_id=gitlab_group_id,
                        description=from_gitlab.description,
                        url=from_gitlab.web_url
                    )
                    self.gitlab_group = new_group
        except:
            pass

    def save(self, *args, **kwargs):
        """Update the save method to fetch fresh info from gitlab when projects are saved."""
        self.fetch_from_gitlab()
        super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.name_with_namespace

class Issue(models.Model):
    """A representation of a user reported issue."""
    title = models.CharField(max_length=200)
    linked_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    linked_user = models.ForeignKey(UserIdentifier, on_delete=models.CASCADE)
    description= models.TextField()
    gitlab_iid = models.IntegerField(null=True, blank=True)
    
    # The following fields related to reviewer status:
    # Django recommends defining choice_list outside of CharField.
    REVIEWER_STATUS_CHOICES = [
        ('P', 'Pending Review'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    ]
    # Reviewer 
    reviewer_status = models.CharField(
        max_length=3,
        choices=REVIEWER_STATUS_CHOICES,
        default='P',  
    )
    # Fields related to GitLab status
    posted_to_GitLab = models.BooleanField(default=False)

    def approve_issue(self):
        """Approve an issue and post to GitLab or return error."""
        # Create the gitlab object
        gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_SECRET_TOKEN)
        # Grab the associated project from gitlab.
        working_project = gl.projects.get(self.linked_project.gitlab_id)
        # Try to create the issue in the gitlab API, saving the newly
        # created issue iid to the model's issue.iid field.
        try:
            new_issue = working_project.issues.create(
                {'title': self.title,
                'description': self.description}
                )
            self.posted_to_GitLab = True
            self.gitlab_iid = new_issue.iid
        except:
            pass

    def save(self, *args, **kwargs):
        if self.reviewer_status == 'A' and self.gitlab_iid == None:
            self.approve_issue() 
        super(Issue, self).save(*args, **kwargs) 

    def __str__(self):
        return self.title

class Note(models.Model):
    """A representation of a note to be created for an issue. """
    # Require a Foreign-Key relationship with a Project object, as notes
    # should only be created for Projects in the database.
    linked_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    linked_user = models.ForeignKey(
        UserIdentifier, on_delete=models.CASCADE)
    # This is the note/comment body.
    body = models.TextField(
        verbose_name='Note Contents',
        help_text="""Type your note body here. You 
            can use <a href='https://docs.gitlab.com/ee/user/markdown.html'
            target="_blank">
            GitLab Flavored Markdown (GFM)</a> on this form.""")
    # issue_iid is not a ForeignKey because Issue objects in database
    # are for issues pending mod approval.
    issue_iid = models.IntegerField()
    # Allow note_id field to be blank as this will be pulled from gitlab.
    gitlab_id = models.IntegerField(blank=True, null=True)
    
    # The following fields related to reviewer status:
    # Django recommends defining choice_list outside of CharField.
    REVIEWER_STATUS_CHOICES = [
        ('P', 'Pending Review'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    ]
    # Reviewer 
    reviewer_status = models.CharField(
        max_length=3,
        choices=REVIEWER_STATUS_CHOICES,
        default='P',  
    )
    # Fields related to GitLab status
    posted_to_GitLab = models.BooleanField(default=False)

    def approve_note(self):
        """Approve a note and post to GitLab or return error."""
        # Create the gitlab object
        gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_SECRET_TOKEN)
        # Grab the associated project from gitlab.
        working_project = gl.projects.get(self.linked_project.gitlab_id)
        # Grab the associated issue from gitlab.
        working_issue = working_project.issues.get(self.issue_iid)
        # Try to create the note in the gitlab API, saving the newly
        # created note id to the note.gitlab_id field.
        try:
            new_note = working_issue.notes.create(
                {'body': self.body,
                }
                )
            self.posted_to_GitLab = True
            self.gitlab_id = new_note.id
        except:
            pass

    def save(self, *args, **kwargs):
        if self.reviewer_status == 'A' and self.gitlab_id == None:
            self.approve_note() 
        super(Note, self).save(*args, **kwargs) 

    def __str__(self):
        return self.body
