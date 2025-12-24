"""
Custom user and password reset token models.

This module defines:
- CustomUser: Extends Django's AbstractUser with role-based access,
  phone number support, and reader subscription relationships.
- ResetToken: Stores time-bound password reset tokens for users.

These models support role-based access control and reader subscriptions
to publishers and journalists.
"""

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

# from news.models import Article, Publisher, Newsletter


# Create your models here.
class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Enhancements:
    - Adds a role field to support Reader, Editor, and Journalist roles.
    - Enforces unique email addresses.
    - Supports optional phone numbers.
    - Enables reader subscriptions to publishers and journalists.
    """

    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='reader'
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    reader_publisher_subscriptions = models.ManyToManyField(
        'news.Publisher', blank=True
    )
    reader_journalist_subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        limit_choices_to={'role': 'journalist'},
        blank=True,
    )

    def save(self, *args, **kwargs):
        """
        Persist the user instance and enforce role-based constraints.

        If the user's role is not 'reader', all reader-specific
        subscription relationships are cleared.
        """

        super().save(*args, **kwargs)

        # remove subscriptions for non-readers
        if self.role in ['journalist', 'editor']:
            self.reader_publisher_subscriptions.clear()
            self.reader_journalist_subscriptions.clear()


class ResetToken(models.Model):
    """
    Model for managing password reset tokens.

    Each token is associated with a user and has an expiry date
    and usage status to prevent reuse.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    token = models.CharField(max_length=500)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)
