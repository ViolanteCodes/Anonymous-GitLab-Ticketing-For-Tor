# Generated by Django 3.1.5 on 2021-01-18 17:19

import anonticket.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anonticket', '0026_note_gitlab_issue_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitlabAccountRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.SlugField(help_text='Type your requested username here. Note that usernames\n        can only use letters, numbers, underscores (_), and hyphens(-).', max_length=64, unique=True, validators=[anonticket.models.check_if_user_in_gitlab])),
                ('email', models.EmailField(max_length=254)),
                ('reason', models.CharField(help_text='Please explain why you want to collaborate with the \n        Tor Community.', max_length=256)),
                ('reviewer_status', models.CharField(choices=[('P', 'Pending Review'), ('A', 'Approved'), ('R', 'Rejected')], default='P', max_length=3)),
                ('approved_to_GitLab', models.BooleanField(default=False)),
            ],
        ),
    ]
