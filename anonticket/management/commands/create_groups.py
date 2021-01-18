from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group , Permission
import logging

# Note: If you would like to create more groups than just Moderators,
# you can expand the below GROUPS dictionary.

GROUPS = {
    "Moderators": {
        # Add specific model permissions here.
        "git lab group" : ["view"],
        "project" : ["view"],
        "issue" : ["add","delete","change","view"],
        "note" : ["add","delete","change","view"],
        "user identifier" : ["view"]
    },
    "Account Approvers": {
        # Add specific model permissions here.
        "gitlab account request" : ["add","delete","change","view"],
        "user identifier" : ["view"],
    },
}

class Command(BaseCommand):

    help = "Creates read only default permission groups for users"

    def handle(self, *args, **options):

        for group_name in GROUPS:

            new_group, created = Group.objects.get_or_create(name=group_name)
            print(f"Creating {group_name}")
            # Loop models in group
            for app_model in GROUPS[group_name]:

                # Loop permissions in group/model
                for permission_name in GROUPS[group_name][app_model]:

                    # Generate permission name as Django would generate it
                    name = "Can {} {}".format(permission_name, app_model)
                    print("Adding Permission {}".format(name))

                    try:
                        model_add_perm = Permission.objects.get(name=name)
                    except Permission.DoesNotExist:
                        logging.warning("Permission not found with name '{}'.".format(name))
                        continue
                    new_group.permissions.add(model_add_perm)