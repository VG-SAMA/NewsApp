"""
Serializers for the News application API.

Includes:
- ArticleSerializer: Serializes Article objects for API responses.
- MySubscriptionsSerializer: Serializes a reader's subscriptions (publishers and journalists).
"""

from rest_framework import serializers
from news.models import Article
from accounts.models import CustomUser


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model.

    Fields:
        - made_by_journalist: The username of the journalist who created the article (read-only).
        - title: Article title.
        - content: Article content.
        - is_independant: Boolean indicating if article is independent.
        - publisher: Publisher name (read-only).
        - is_approved: Boolean indicating if the article is approved by an editor.
        - created_at: Timestamp of article creation.
    """

    publisher = serializers.StringRelatedField(read_only=True)
    made_by_journalist = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Article
        fields = [
            'made_by_journalist',
            'title',
            'content',
            'is_independant',
            'publisher',
            'is_approved',
            'created_at',
        ]


class MySubscriptionsSerializer(serializers.ModelSerializer):
    """
    Serializer for a reader's subscriptions.

    Provides a read-only view of the user's subscribed journalists and publishers.

    Fields:
        - reader_journalist_subscriptions: List of usernames of subscribed journalists.
        - reader_publisher_subscriptions: List of names of subscribed publishers.
    """

    reader_journalist_subscriptions = serializers.StringRelatedField(
        many=True, read_only=True
    )
    reader_publisher_subscriptions = serializers.StringRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'reader_journalist_subscriptions',
            'reader_publisher_subscriptions',
        ]


"""
References:
https://www.django-rest-framework.org/api-guide/relations/
https://stackoverflow.com/questions/61143864/django-rest-framework-serialize-user-manytomany-field-by-username
https://stackoverflow.com/questions/62302668/django-serializer-manytomany-retrun-array-of-names-instead-of-an-array-of-ids
https://stackoverflow.com/questions/62302668/django-serializer-manytomany-retrun-array-of-names-instead-of-an-array-of-ids#:~:text=Sorted%20by:,2%2C8792%2033%2047
https://www.reddit.com/r/djangolearning/comments/tarafk/drf_show_name_instead_of_a_foreign_key_number/?rdt=52419
https://www.moesif.com/blog/technical/api-development/Django-REST-API-Tutorial/#:~:text=Django%20REST%20framework%20(DRF)%20stands,helps%20in%20reducing%20code%20redundancy.
https://www.django-rest-framework.org/#:~:text=Django%20REST%20framework%20is%20a,Hat%2C%20Heroku%2C%20and%20Eventbrite.
https://www.youtube.com/watch?v=t-uAgI-AUxc&t=698s


"""
