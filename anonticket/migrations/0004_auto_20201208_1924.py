# Generated by Django 3.1.4 on 2020-12-08 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('anonticket', '0003_anonuser_user_identifer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='linked_user',
            field=models.ForeignKey(default='testtesttesttesttest', on_delete=django.db.models.deletion.CASCADE, to='anonticket.anonuser'),
        ),
    ]
