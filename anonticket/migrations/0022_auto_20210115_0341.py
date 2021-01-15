# Generated by Django 3.1.5 on 2021-01-15 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anonticket', '0021_auto_20210111_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='issue_title',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='gitlabgroup',
            name='name',
            field=models.CharField(blank=True, help_text="IMPORTANT: GLGROUPS are AUTOMATICALLY CREATED when a project requiring\n    the group has been added--so you shouldn't have to do anything here!", max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='body',
            field=models.TextField(help_text='Type your note body here. You \n            can use <a href=\'https://docs.gitlab.com/ee/user/markdown.html\'\n            target="_blank">\n            GitLab Flavored Markdown (GFM)</a> on this form.', verbose_name='Note Contents'),
        ),
        migrations.AlterField(
            model_name='project',
            name='gitlab_id',
            field=models.IntegerField(help_text="IMPORTANT: Enter a \n    gitlab ID into this field and save, and the project's details will \n    be fetched from gitlab! NOTHING ELSE ON THIS FORM NEEDS TO BE \n    FILLED IN. Additionally, if a project is saved, a fresh copy of\n    the gitlab details will be fetched and the database entries will\n    be updated."),
        ),
    ]
