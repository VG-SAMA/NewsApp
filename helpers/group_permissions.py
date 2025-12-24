"""
Utility functions for creating default user groups and permissions.

This module defines a helper function that initializes role-based
Django auth groups and assigns model-level permissions for the
News application.

The function is idempotent and safe to call multiple times, making it
suitable for use in signals, management commands, or startup hooks.
"""

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def make_groups_and_permissions():
    """
    Create default user groups and assign permissions.

    This function:
    - Creates predefined role-based groups if they do not exist
    - Retrieves content types for core News models
    - Assigns appropriate CRUD permissions per role

    The function is safe to call multiple times and will exit early
    if permissions have not yet been created by Django migrations.

    Intended roles:
    - Reader: Can view articles
    - Editor: Can review and manage articles and newsletters
    - Journalist: Can create and manage their own content
    - Manage_Publishers: Full control over publisher entities
    """

    # Create groups
    reader_group, _ = Group.objects.get_or_create(name="Reader")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")
    publisher_group, _ = Group.objects.get_or_create(name="Manage_Publishers")

    # Get models
    Article = apps.get_model("news", "Article")
    Newsletter = apps.get_model("news", "Newsletter")
    Publisher = apps.get_model("news", "Publisher")

    # Content types
    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)
    publishers_ct = ContentType.objects.get_for_model(Publisher)

    # Fetch permissions
    article_perms = Permission.objects.filter(
        content_type=article_ct,
        codename__in=[
            "add_article",
            "view_article",
            "change_article",
            "delete_article",
        ],
    )

    newsletter_perms = Permission.objects.filter(
        content_type=newsletter_ct,
        codename__in=[
            "add_newsletter",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
        ],
    )

    publisher_perms = Permission.objects.filter(
        content_type=publishers_ct,
        codename__in=[
            "add_publisher",
            "view_publisher",
            "change_publisher",
            "delete_publisher",
        ],
    )

    # If permissions are not ready yet then return
    if (
        article_perms.count() < 4
        or newsletter_perms.count() < 4
        or publisher_perms.count() < 4
    ):
        return

    article_perm_map = {p.codename: p for p in article_perms}
    newsletter_perm_map = {p.codename: p for p in newsletter_perms}
    publisher_perm_map = {p.codename: p for p in publisher_perms}

    # Assign permissions
    reader_group.permissions.add(article_perm_map["view_article"])

    editor_group.permissions.add(
        article_perm_map["view_article"],
        article_perm_map["change_article"],
        article_perm_map["delete_article"],
        newsletter_perm_map["view_newsletter"],
        newsletter_perm_map["change_newsletter"],
        newsletter_perm_map["delete_newsletter"],
    )

    journalist_group.permissions.add(
        article_perm_map["add_article"],
        article_perm_map["view_article"],
        article_perm_map["change_article"],
        article_perm_map["delete_article"],
        newsletter_perm_map["add_newsletter"],
        newsletter_perm_map["view_newsletter"],
        newsletter_perm_map["change_newsletter"],
        newsletter_perm_map["delete_newsletter"],
    )

    publisher_group.permissions.add(
        publisher_perm_map["add_publisher"],
        publisher_perm_map["view_publisher"],
        publisher_perm_map["change_publisher"],
        publisher_perm_map["delete_publisher"],
    )
