# Generated by Django 3.1.5 on 2021-01-27 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anonticket', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitlabaccountrequest',
            name='linked_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='anonticket.useridentifier'),
        ),
    ]