from django.db import models

# Create your models here.

class AnonUser(models.Model):
    """Representation of a user identifier."""
    user_identifer = ""

    def publish(self):
        self.save()

    def __str__(self):
        return self.user_identifer

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
    linked_user = models.ForeignKey(AnonUser, on_delete=models.CASCADE)
    issue_description= models.TextField()
    
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

    def publish(self):
        self.save()

    def __str__(self):
        return self.issue_title
