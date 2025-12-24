"""
Database models for the News application.

This module defines the core data structures used throughout the system:
- Publisher: Represents a news publishing organization
- Article: Represents a news article written by a journalist
- Newsletter: Represents a curated collection of articles

These models enforce relationships between journalists, editors,
publishers, and readers, and support both independent and
publisher-affiliated content.
"""

from django.db import models
from django.conf import settings
from model_utils import FieldTracker


class Publisher(models.Model):
    """
    Represents a news publisher organization.

    A publisher can have multiple journalists and editors associated
    with it. Publishers are responsible for approving and distributing
    articles and newsletters created under their organization.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        limit_choices_to={'role': 'journalist'},
        related_name='publisher_journalists',
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        limit_choices_to={'role': 'editor'},
        related_name='publisher_editors',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the publisher.

        :return: Publisher name
        """

        return self.name


class Article(models.Model):
    """
    Represents a news article written by a journalist.

    Articles may be:
    - Independent (written and published directly by a journalist)
    - Publisher-affiliated (requiring editorial approval)

    Articles support approval workflows and publication metadata.
    """

    made_by_journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='articles_made',
        null=True,
    )
    title = models.CharField(max_length=255)
    content = models.TextField()

    is_independant = models.BooleanField(default=False)
    approved_by_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='articles_approved',
    )

    is_approved = models.BooleanField(default=False)
    date_edited = models.DateTimeField(blank=True, null=True)

    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, blank=True, null=True
    )

    date_published = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    tracker = FieldTracker()

    def __str__(self) -> str:
        """
        Return a readable representation of the article.

        :return: Article title and journalist username
        """

        return f'{self.title}, {self.made_by_journalist.username}'


class Newsletter(models.Model):
    """
    Represents a newsletter containing a curated collection of articles.

    Newsletters can be:
    - Independent (created by a journalist)
    - Publisher-affiliated (distributed by a publisher)

    Readers gain access to newsletters based on their subscriptions.
    """

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='newsletters_published',
    )
    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        limit_choices_to={'role': 'journalist'},
        related_name='newsletters_made',
    )

    title = models.CharField(max_length=255)
    articles = models.ManyToManyField(
        Article, related_name='articles_included'
    )

    is_independant = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Return a human-readable representation of the newsletter.

        :return: Newsletter title
        """

        return f'{self.title}'
