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

class GLGroup(models.Model):
    """Representation of a Gitlab Group in the database. This does not
    need to be supplied by the admin; it will automatically be created if
    a project is put into the database."""
    name = models.CharField(max_length=200, null=True, blank=True)
    gl_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    """Representation of a project in the database. To add a GL project 
    to the database, only the gitlab id number needs to be supplied in the
    project_id field. Upon saving, the project details and any necessary
    group details will be fetched from gitlab."""
    project_id = models.IntegerField()
    project_name = models.CharField(max_length=200, null=True, blank=True)
    project_name_with_namespace = models.CharField(max_length=200, null=True, blank=True)
    project_description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=50, null=True, blank=True)
    project_url = models.URLField(null=True, blank=True)
    project_gl_group = models.ForeignKey(GLGroup, on_delete=models.CASCADE, null=True, blank=True)

    def fetch_from_gitlab(self):
        """Given the project_id, fetch the relevant information from Gitlab."""
        # Create the gitlab object
        gl = gitlab.Gitlab(settings.GITLAB_URL, private_token=settings.GITLAB_SECRET_TOKEN)
        # Grab the associated project from gitlab.
        try: 
            working_project = gl.projects.get(self.project_id)
            self.project_name = working_project.name
            self.project_name_with_namespace = working_project.name_with_namespace
            self.project_description = working_project.description 
            self.slug = slugify(working_project.name)
            self.project_url = working_project.web_url
        # if the project does not have a project_gl_group foreignkey, first
        # check to see if a GLGroup object with the gitlab id exists.
            if not self.project_gl_group:
                gl_group_id = working_project.namespace['id']
                try:
                    fetch_group = GLGroup.objects.get(gl_id=gl_group_id)
                    self.project_gl_group = fetch_group
        # if a matching GlGroup cannot be fetched, pull the group info from
        # gitlab and create one.
                except:
                    from_gitlab = gl.groups.get(gl_group_id)
                    new_group = GLGroup.objects.create(
                        name=from_gitlab.name,
                        gl_id=gl_group_id,
                        description=from_gitlab.description,
                        url=from_gitlab.web_url
                    )
                    self.project_gl_group = new_group
        except:
            pass

    def save(self, *args, **kwargs):
        """Update the save method to fetch fresh info from gitlab when projects are saved."""
        self.fetch_from_gitlab()
        super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.project_name

class Issue(models.Model):
    """A representation of a user reported issue."""
    issue_title = models.CharField(max_length=200)
    linked_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    linked_user = models.ForeignKey(UserIdentifier, on_delete=models.CASCADE, default=1)
    issue_description= models.TextField()
    issue_iid = models.IntegerField(null=True, blank=True)
    
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
        working_project = gl.projects.get(self.linked_project.project_id)
        # Try to create the issue in the gitlab API, saving the newly
        # created issue iid to the model's issue.iid field.
        try:
            new_issue = working_project.issues.create(
                {'title': self.issue_title,
                'description': self.issue_description}
                )
            self.posted_to_GitLab = True
            self.issue_iid = new_issue.iid
        except:
            pass

    def save(self, *args, **kwargs):
        if self.reviewer_status == 'A' and self.issue_iid == None:
            self.approve_issue() 
        super(Issue, self).save(*args, **kwargs) 

    def __str__(self):
        return self.issue_title
