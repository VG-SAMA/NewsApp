from django.test import TestCase
from django.contrib.auth import get_user_model
from news.models import Article, Publisher
from rest_framework.test import APIClient

CustomUser = get_user_model()


class ArticleAPITests(TestCase):
    def setUp(self):
        # Create users
        self.journalist = CustomUser.objects.create_user(
            username="journalist1",
            email="journalist1@example.com",
            password="pass1234",
            role="journalist",
        )
        self.reader = CustomUser.objects.create_user(
            username="reader1",
            email="reader1@example.com",
            password="pass1234",
            role="reader",
        )

        # Create publishers
        self.publisher1 = Publisher.objects.create(name="Publisher 1")
        self.publisher2 = Publisher.objects.create(name="Publisher 2")

        # Link journalist to publisher1
        self.publisher1.journalists.add(self.journalist)

        # Subscribe reader to journalist and publisher1
        self.reader.reader_journalist_subscriptions.add(self.journalist)  # type: ignore
        self.reader.reader_publisher_subscriptions.add(self.publisher1)  # type: ignore

        # Create articles
        self.article_indep = Article.objects.create(
            title="Independent Article",
            content="Content indep",
            is_independant=True,
            is_approved=True,
            made_by_journalist=self.journalist,
        )

        self.article_pub = Article.objects.create(
            title="Publisher Article",
            content="Content pub",
            is_independant=False,
            is_approved=True,
            publisher=self.publisher1,
            made_by_journalist=self.journalist,
        )

        self.article_unsub_pub = Article.objects.create(
            title="Other Publisher Article",
            content="Content unsub",
            is_independant=False,
            is_approved=True,
            publisher=self.publisher2,
            made_by_journalist=self.journalist,
        )

        # Setup API client and login
        self.client = APIClient()
        self.client.login(username="reader1", password="pass1234")

    def test_article_list_returns_subscribed_articles(self):
        response = self.client.get("/api/articles/")
        data = response.json()
        titles = [a["title"] for a in data]

        # Reader should see independent + subscribed publisher articles
        self.assertIn("Independent Article", titles)
        self.assertIn("Publisher Article", titles)
        self.assertNotIn("Other Publisher Article", titles)

    def test_article_list_excludes_unsubscribed(self):
        response = self.client.get("/api/articles/")
        data = response.json()
        titles = [a["title"] for a in data]

        # Article from publisher2 is not subscribed, should not appear
        self.assertNotIn("Other Publisher Article", titles)


class MySubscriptionsAPITests(TestCase):
    def setUp(self):
        # Create users
        self.journalist = CustomUser.objects.create_user(
            username="journalist1",
            email="journalist1@example.com",
            password="pass1234",
            role="journalist",
        )
        self.reader = CustomUser.objects.create_user(
            username="reader1",
            email="reader1@example.com",
            password="pass1234",
            role="reader",
        )

        # Subscribe reader
        self.reader.reader_journalist_subscriptions.add(self.journalist)  # type: ignore

        # Setup API client
        self.client = APIClient()
        self.client.login(username="reader1", password="pass1234")

    def test_my_subscriptions_returns_correct_data(self):
        response = self.client.get("/api/my-subscriptions/")
        data = response.json()
        self.assertEqual(
            data[0]["reader_journalist_subscriptions"][0], str(self.journalist)
        )
