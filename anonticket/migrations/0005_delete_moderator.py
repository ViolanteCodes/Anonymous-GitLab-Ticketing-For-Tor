# Generated by Django 3.1.4 on 2020-12-21 20:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('anonticket', '0004_moderator'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Moderator',
        ),
    ]
