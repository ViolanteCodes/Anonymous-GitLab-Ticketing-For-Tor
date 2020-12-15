from django.db import models
from django.conf import settings
import gitlab

# Create your models here.

class UserIdentifier(models.Model):
    """Representation of a user identifier."""
    user_identifier = models.CharField(max_length=200)

    def publish(self):
        self.save()

    def __str__(self):
        return self.user_identifier

class Project(models.Model):
    """Representation of a project in the database."""
    project_name = models.CharField(max_length=200)
    project_description = models.TextField()
    project_slug = models.SlugField(max_length=50)
    project_id = models.IntegerField()

    def publish(self):
        self.save()

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


