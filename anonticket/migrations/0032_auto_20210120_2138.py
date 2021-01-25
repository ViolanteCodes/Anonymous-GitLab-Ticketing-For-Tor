# Generated by Django 3.1.5 on 2021-01-20 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anonticket', '0031_auto_20210120_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='mod_comment',
            field=models.TextField(blank=True, help_text='As a moderator, you can add a comment to this item. \n        Once saved, it will appear on the moderator landing page and can\n        be seen by all moderators, but it will not be seen by users. ', verbose_name='Moderator Comment'),
        ),
    ]