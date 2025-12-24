"""
Form definitions for the News application.

This module contains Django ModelForms used to create, update,
and manage articles, publishers, newsletters, and reader subscriptions.

Forms implement role-based behavior and validation logic for:
- Journalists
- Editors
- Readers
"""

from django import forms
from .models import Article, Publisher, Newsletter
from typing import cast  # type: ignore
from django.db.models import Q
from accounts.models import CustomUser


class ArticleForm(forms.ModelForm):
    """
    Form used to create and update Article instances.

    Behavior differs depending on the role:
    - Journalists can create and edit articles and choose publishers
    - Editors can only approve or unapprove existing articles

    Validation ensures correct handling of independent vs
    publisher-affiliated articles.
    """

    class Meta:
        model = Article
        fields = [
            'title',
            'content',
            'is_independant',
            'publisher',
            'is_approved',
        ]

    def __init__(self, *args, **kwargs):
        """
        Initialize the ArticleForm.

        Supports two modes:
        - Editor mode: hides publisher and independence fields
        - Journalist mode: filters available publishers based on affiliation

        Args:
            user (CustomUser, optional): The logged-in user.
            editor (bool, optional): Enables editor-only behavior.
        """

        self.user = kwargs.pop('user', None)
        self.editor_mode = kwargs.pop('editor', False)
        super().__init__(*args, **kwargs)

        if self.editor_mode:
            # Editors can only approve/unapprove
            self.fields['publisher'].widget = forms.HiddenInput()
            self.fields['is_independant'].widget = forms.HiddenInput()

            # Set initial values so form still has them
            if self.instance and self.instance.publisher:
                self.fields['publisher'].initial = self.instance.publisher
            if self.instance:
                self.fields['is_independant'].initial = (
                    self.instance.is_independant
                )

        else:
            # Journalist logic: only show publishers relevant to the user
            self.fields['publisher'].queryset = Publisher.objects.none()  # type: ignore
            if self.user:
                user_publishers = Publisher.objects.filter(
                    journalists=self.user
                )
                if self.instance and self.instance.publisher:
                    # Include current publisher even if not in user list
                    user_publishers = Publisher.objects.filter(
                        Q(journalists=self.user)
                        | Q(id=self.instance.publisher.id)
                    ).distinct()
                self.fields['publisher'].queryset = user_publishers  # type: ignore

    def clean(self):
        """
        Perform cross-field validation.

        Enforces the following rules:
        - Independent articles cannot be linked to a publisher
        - Publisher-affiliated articles must have a publisher selected
        - Editor mode preserves hidden field values

        Returns:
            dict: Cleaned form data.

        Raises:
            ValidationError: If validation rules are violated.
        """

        cleaned_data = super().clean()

        if self.editor_mode:
            # Preserve hidden fields for editor
            if self.instance:
                cleaned_data['publisher'] = self.instance.publisher
                cleaned_data['is_independant'] = self.instance.is_independant
        else:
            # Journalist validation
            is_independant = cleaned_data.get('is_independant')
            publisher = cleaned_data.get('publisher')

            if is_independant and publisher:
                raise forms.ValidationError(
                    "Independent articles cannot be linked to a publisher."
                )
            if not is_independant and not publisher:
                raise forms.ValidationError(
                    "Non-independent articles must have a publisher."
                )

        return cleaned_data


class PublisherForm(forms.ModelForm):
    """
    Form used to create and update Publisher instances.

    Allows administrators or managers to assign journalists
    and editors to a publisher.
    """

    class Meta:
        model = Publisher
        fields = ['name', 'description', 'journalists', 'editors']


class NewsletterForm(forms.ModelForm):
    """
    Form used by journalists to create and update newsletters.

    Supports both:
    - Independent newsletters
    - Publisher-affiliated newsletters

    Articles are dynamically filtered based on newsletter type
    and approval status.
    """

    class Meta:
        model = Newsletter
        fields = ['title', 'is_independant', 'publisher', 'articles']

    def __init__(self, *args, **kwargs):
        """
        Initialize the NewsletterForm.

        Filters available articles and publishers based on:
        - Newsletter independence
        - Logged-in journalist

        Args:
            user (CustomUser, optional): The logged-in journalist.
        """

        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Hide publisher if independant
        if self.instance and self.instance.is_independant:
            self.fields['publisher'].widget = forms.HiddenInput()

        # Initially filter articles
        if self.instance and self.instance.is_independant:
            self.fields['articles'].queryset = Article.objects.filter(  # type: ignore
                made_by_journalist=self.user
            )
        else:
            self.fields['articles'].queryset = Article.objects.filter(  # type: ignore
                Q(is_approved=True)
            )

            # new
            self.fields['publisher'].queryset = Publisher.objects.filter(  # type: ignore
                Q(journalists=self.user)
            )

    def clean(self):
        """
        Validate newsletter data.

        Rules:
        - Independent newsletters must not have a publisher
        - Publisher newsletters must have a publisher selected

        Returns:
            dict: Cleaned form data.

        Raises:
            ValidationError: If publisher requirements are violated.
        """

        cleaned_data = super().clean()
        is_independant = cleaned_data.get('is_independant')
        publisher = cleaned_data.get('publisher')

        if is_independant:
            # Independent newsletter should not have a publisher
            cleaned_data['publisher'] = None
        else:
            if not publisher:
                raise forms.ValidationError(
                    "Publisher newsletters must have a publisher selected."
                )

        return cleaned_data


class EditorNewsletterForm(forms.ModelForm):
    """
    Form used by editors to update newsletters.

    Editors can modify the newsletter title and
    manage which approved articles are included.
    """

    class Meta:
        model = Newsletter
        fields = ['title', 'articles']

    def __init__(self, *args, **kwargs):
        """
        Initialize the editor newsletter form.

        Limits selectable articles to approved articles
        belonging to the newsletter's publisher.
        """

        super().__init__(*args, **kwargs)

        # only approved articles for this publisher
        if self.instance.pk and self.instance.publisher:
            self.fields['articles'].queryset = Article.objects.filter(  # type: ignore
                publisher=self.instance.publisher, is_approved=True
            )
        else:
            self.fields['articles'].queryset = Article.objects.none()  # type: ignore


class ReaderSubscriptionForm(forms.ModelForm):
    """
    Form allowing readers to manage their subscriptions.

    Readers can subscribe to:
    - Publishers
    - Individual journalists
    """

    class Meta:
        model = CustomUser
        fields = [
            "reader_publisher_subscriptions",
            "reader_journalist_subscriptions",
        ]


"""
References:
https://docs.djangoproject.com/en/6.0/topics/forms/
https://docs.djangoproject.com/en/6.0/ref/forms/validation/


"""
