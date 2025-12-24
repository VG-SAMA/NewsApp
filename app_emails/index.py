"""
Notification utilities for published articles.

This module handles:
- Sending HTML email notifications to subscribed readers
- Posting automated tweets when an article is published

Emails are sent using Django's EmailMultiAlternatives.
Tweets are posted using a custom TwitterAutomation client.

This logic is typically triggered from Django signals.
"""

from news.models import Article
from accounts.models import CustomUser
from helpers.index import Helpers
from django.core.mail import EmailMultiAlternatives
from twitter import twitter_client

helpers = Helpers()
tweets = twitter_client.TwitterAutomation()


class SendingEmails_SendingTweets:
    """
    Handles sending notification emails and tweets for published articles.

    Responsibilities:
    - Fetch subscribed readers for a publisher
    - Send HTML email notifications
    - Post a tweet announcing the article
    """

    sender_email = 'vidaal702@gmail.com'

    def build_and_send_email(self, content: str, pk: int):
        """
        Build and send notification emails to subscribed readers.

        Also triggers a tweet announcing the article.

        Args:
            content (str): Rendered HTML email content.
            pk (int): Primary key of the Article instance.

        Returns:
            None
        """

        article = Article.objects.get(pk=pk)
        readers_list = CustomUser.objects.filter(
            reader_publisher_subscriptions=article.publisher
        )

        if article and readers_list.exists():
            readers_emails = [reader.email for reader in readers_list]
            subject = (
                f'New Article has been published by {article.publisher.name}'
            )

            print(readers_emails)
            print(article)

            self.make_and_send_tweet(article)

            try:
                for r in readers_emails:
                    try:
                        msg = EmailMultiAlternatives(
                            subject=subject,
                            body='This email requires an HTML-compatible client.',
                            from_email=self.sender_email,
                            to=[r],
                        )

                        msg.attach_alternative(content, 'text/HTML')
                        msg.send()
                    except Exception as e:
                        print(
                            f'Error Occured,  possible email does not exist: {e}'
                        )

            except Exception as e:
                print(f'Error Occurred: {e}')

    def make_and_send_tweet(self, article: Article):
        """
        Create and publish a tweet for a given article.

        Args:
            article (Article): Article instance being announced.

        Returns:
            None
        """

        try:
            message = self.tweet_length(article)

            result = tweets.make_tweet(message['text'], media_id=None)
            print(result)

        except Exception as e:
            print(f'Error Occurred making tweet: {e}')

    def tweet_length(self, article: Article) -> dict:
        """
        Build a tweet message that respects Twitter length limits.

        If the article content exceeds the maximum length, it is truncated
        and a link to the full article is appended.

        Args:
            article (Article): Article to summarize.

        Returns:
            dict: Dictionary containing tweet text.
        """

        """
        This fuction checks the length of the message being posted
        on twitter, becasue there is a certain limit to characters
        that can be posted. I assume becasue its the free service.

        :param article: An article object to access its fields

        :returns: Dictionary so the twitter api can access the 'text' key
        """
        max_length = 150
        content_limit = max_length - 50

        message = {
            "text": (
                f"New Article Published by {article.publisher.name}Test:\n"
                f"Journalist: {article.made_by_journalist.username}\n\n"
                f"Content: {article.content}"
            )
        }

        if len(message['text']) <= max_length:
            return message

        message = {
            'text': (
                f"New Article Published by {article.publisher.name}Test:\n"
                f"Journalist: {article.made_by_journalist.username}\n\n"
                f"Content: {article.content[:content_limit]}...\n"
                f"Read more at: http://127.0.0.1:8000/news/readers/view-article/{article.pk}/"
            )
        }

        return message


# https://www.youtube.com/watch?v=8p4M-7VXhAU
