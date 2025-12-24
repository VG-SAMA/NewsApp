"""
Signal to automatically add new users to their respective groups based on role.

- Ensures the required groups and permissions exist before assigning.
- Automatically assigns superusers to the Manage_Publishers group.

References:
https://www.youtube.com/watch?v=8p4M-7VXhAU
"""

from accounts.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from helpers.group_permissions import make_groups_and_permissions
from django.contrib.auth.models import Group


@receiver(post_save, sender=CustomUser)
def add_user_to_groups(sender, instance: CustomUser, created: bool, **kwargs):
    """
    Add newly created users to the appropriate group.

    Args:
        sender: The model class (CustomUser)
        instance: The instance of the user created
        created: Boolean flag indicating if the instance is new
        **kwargs: Additional arguments

    Notes:
        - Superusers are automatically added to 'Manage_Publishers'
        - Readers, Journalists, and Editors are assigned to their respective groups
    """

    if not created:
        return

    # Ensure groups and permissions exist
    make_groups_and_permissions()

    if instance.is_superuser:
        group, _ = Group.objects.get_or_create(name="Manage_Publishers")
        instance.groups.add(group)
        return

    role_group_map = {
        "reader": "Reader",
        "journalist": "Journalist",
        "editor": "Editor",
    }

    group_name = role_group_map.get(instance.role)
    if not group_name:
        return

    # Add user to the corresponding group
    group, _ = Group.objects.get_or_create(name=group_name)
    instance.groups.add(group)
