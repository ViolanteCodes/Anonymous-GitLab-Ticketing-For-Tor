# Generated by Django 3.1.4 on 2021-01-07 23:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anonticket', '0010_auto_20210107_2047'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='project_id',
            new_name='gitlab_id',
        ),
    ]
