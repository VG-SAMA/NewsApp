"""
API views for the News application.

Includes:
- ArticleListAPIView: Provides a list of approved articles accessible to the authenticated reader.
- MySubscriptionListAPIView: Provides a reader's current subscriptions (publishers and journalists).

Permissions:
- Only authenticated users with the role 'reader' can access these endpoints.
"""

from rest_framework import generics  # , viewsets
from news.models import Article
from .serializers import ArticleSerializer, MySubscriptionsSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsReader
from django.db.models import Q
from accounts.models import CustomUser


# Create your views here.
class ArticleListAPIView(generics.ListAPIView):
    """
    API endpoint that returns a list of approved articles available to the reader.

    The queryset filters:
        - Non-independent articles published by publishers the reader is subscribed to.
        - Independent articles made by journalists the reader is subscribed to.
    """

    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsReader]

    def get_queryset(self):
        user = self.request.user

        all_articles = (
            Article.objects.filter(is_approved=True)
            .filter(
                Q(
                    is_independant=False,
                    publisher__in=user.reader_publisher_subscriptions.all(),  # type: ignore
                )
                | Q(
                    is_independant=True,
                    made_by_journalist__in=user.reader_journalist_subscriptions.all(),  # type: ignore
                )
            )
            .distinct()
        )

        return all_articles


class MySubscriptionListAPIVIew(generics.ListAPIView):
    """
    API endpoint that returns the subscriptions of the authenticated reader.

    Returns:
        - reader_journalist_subscriptions: List of usernames of subscribed journalists.
        - reader_publisher_subscriptions: List of names of subscribed publishers.
    """

    serializer_class = MySubscriptionsSerializer
    permission_classes = [IsAuthenticated, IsReader]

    def get_queryset(self):
        return CustomUser.objects.filter(pk=self.request.user.pk)
