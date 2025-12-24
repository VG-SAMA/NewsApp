"""
Signals file to handle user groups
creations and sending emails and tweeits when
a publisher article is approved.
"""

from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from helpers.group_permissions import make_groups_and_permissions
from news.models import Article
from app_emails.index import SendingEmails_SendingTweets  # , async_emails
from django.template.loader import render_to_string


@receiver(post_migrate)
def create_groups_and_assign_permissions(sender, **kwargs):
    """
    Create default user groups and assign permissions.
    """

    """
    # Run  news app only
    if sender.name != "news":
        return

    # Create groups
    reader_group, _ = Group.objects.get_or_create(name="Reader")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")

    # Get models
    Article = apps.get_model("news", "Article")
    Newsletter = apps.get_model("news", "Newsletter")

    # Content types
    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    # Fetch permissions safely
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

    # If permissions not ready yet, try again next migrate/run
    if article_perms.count() < 4 or newsletter_perms.count() < 4:
        os.system("clear all")
        print(
            "Permissions could not be made correctly please run 'python manage.py migrate' again to create the permissions "
        )
        return

    # Map permissions
    article_perm_map = {p.codename: p for p in article_perms}
    newsletter_perm_map = {p.codename: p for p in newsletter_perms}

    # Reader permissions
    reader_group.permissions.add(article_perm_map["view_article"])

    # Editor permissions
    editor_group.permissions.add(
        article_perm_map["view_article"],
        article_perm_map["change_article"],
        article_perm_map["delete_article"],
        newsletter_perm_map["view_newsletter"],
        newsletter_perm_map["change_newsletter"],
        newsletter_perm_map["delete_newsletter"],
    )

    # Journalist permissions
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
"""

    make_groups_and_permissions()


@receiver(post_save, sender=Article)
def email_publisher_article(sender, instance, created, **kwargs):
    """
    Send email and tweet notifications when an article is approved.

    This signal is triggered after an Article instance is saved.
    Notifications are only sent when:
    - The article already existed (not created)
    - The `is_approved` field has changed
    - The new value of `is_approved` is True

    Args:
        sender (Model): The model class sending the signal.
        instance (Article): The saved Article instance.
        created (bool): Indicates if the instance was created.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """

    if not created:
        if (
            (instance.tracker.previous('is_approved') == False)
            and (instance.tracker.has_changed('is_approved'))
            and (instance.is_approved == True)
        ):
            print('EMAIL WILL BE SENT')

            try:
                my_email_obj = SendingEmails_SendingTweets()

                email_content = render_to_string(
                    'news/email/email_approved_template.html',
                    {
                        'article': instance,
                        'article_url': f'http://127.0.0.1:8000/news/readers/view-article/{instance.pk}/',
                    },
                )

                my_email_obj.build_and_send_email(email_content, instance.pk)

            except Exception as e:
                print(f'Error occured in signals file: {e}')

        else:
            print('EMAIL WILL NOT BE SENT!!!!!')
