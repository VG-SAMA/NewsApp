from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from news.models import Article, Publisher, Newsletter
from rest_framework.test import APIClient

CustomUser = get_user_model()


class ReaderViewsTests(TestCase):
    def setUp(self):
        # Create groups
        self.reader_group, _ = Group.objects.get_or_create(name="Reader")

        # Create users
        self.reader = CustomUser.objects.create_user(
            username="reader1",
            email="reader1@example.com",
            password="pass1234",
            role="reader",
        )
        self.reader.groups.add(self.reader_group)

        self.journalist = CustomUser.objects.create_user(
            username="journalist1",
            email="journalist1@example.com",
            password="pass1234",
            role="journalist",
        )

        # Create publishers
        self.publisher1 = Publisher.objects.create(name="Publisher 1")
        self.publisher2 = Publisher.objects.create(name="Publisher 2")

        # Link journalist to publisher1
        self.publisher1.journalists.add(self.journalist)

        # Subscribe reader
        self.reader.reader_journalist_subscriptions.add(self.journalist)  # type: ignore
        self.reader.reader_publisher_subscriptions.add(self.publisher1)  # type: ignore

        # Create articles
        self.article_indep = Article.objects.create(
            title="Independent Article",
            content="Independent content",
            is_independant=True,
            is_approved=True,
            made_by_journalist=self.journalist,
        )

        self.article_pub = Article.objects.create(
            title="Publisher Article",
            content="Publisher content",
            is_independant=False,
            is_approved=True,
            publisher=self.publisher1,
            made_by_journalist=self.journalist,
        )

        self.article_unsub = Article.objects.create(
            title="Unsubscribed Publisher Article",
            content="Unsub content",
            is_independant=False,
            is_approved=True,
            publisher=self.publisher2,
            made_by_journalist=self.journalist,
        )

        # Create newsletters
        self.newsletter_indep = Newsletter.objects.create(
            title="Independent Newsletter",
            is_independant=True,
            journalist=self.journalist,
        )
        self.newsletter_indep.articles.add(self.article_indep)

        self.newsletter_pub = Newsletter.objects.create(
            title="Publisher Newsletter",
            is_independant=False,
            publisher=self.publisher1,
        )
        self.newsletter_pub.articles.add(self.article_pub)

        self.newsletter_unsub = Newsletter.objects.create(
            title="Unsubscribed Newsletter",
            is_independant=False,
            publisher=self.publisher2,
        )
        self.newsletter_unsub.articles.add(self.article_unsub)

        # Login the reader
        self.client.login(username="reader1", password="pass1234")

    def test_dashboard_shows_correct_articles(self):
        url = reverse("news:readers_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        articles = response.context["articles"]
        self.assertIn(self.article_indep, articles)
        self.assertIn(self.article_pub, articles)
        self.assertNotIn(self.article_unsub, articles)

    def test_dashboard_search_query(self):
        url = reverse("news:readers_dashboard") + "?q=Independent"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        articles = response.context["articles"]
        self.assertIn(self.article_indep, articles)
        self.assertNotIn(self.article_pub, articles)

    def test_view_article(self):
        url = reverse(
            "news:readers_view_article", args=[self.article_indep.pk]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["article"], self.article_indep)

    def test_view_article_404(self):
        url = reverse("news:readers_view_article", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_newsletter_dashboard_shows_correct_newsletters(self):
        url = reverse("news:readers_news_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        newsletters = response.context["newsletters"]
        self.assertIn(self.newsletter_indep, newsletters)
        self.assertIn(self.newsletter_pub, newsletters)
        self.assertNotIn(self.newsletter_unsub, newsletters)

    def test_view_newsletter(self):
        url = reverse(
            "news:readers_view_newsletter", args=[self.newsletter_indep.pk]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["newsletter"], self.newsletter_indep)

    def test_view_newsletter_404(self):
        url = reverse("news:readers_view_newsletter", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_manage_subscriptions_get_form(self):
        url = reverse("news:readers_manage_subscriptions")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_manage_subscriptions_post_updates(self):
        url = reverse("news:readers_manage_subscriptions")
        data = {"reader_publisher_subscriptions": [self.publisher2.pk]}
        response = self.client.post(url, data)
        self.reader.refresh_from_db()
        self.assertIn(
            self.publisher2, self.reader.reader_publisher_subscriptions.all()  # type: ignore
        )
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)


class EditorViewsTests(TestCase):
    def setUp(self):
        # Create an editor
        self.editor = CustomUser.objects.create_user(
            username="editor1",
            email="editor1@example.com",
            password="pass1234",
            role="editor",
        )

        # Create another editor for negative tests
        self.other_editor = CustomUser.objects.create_user(
            username="editor2",
            email="editor2@example.com",
            password="pass1234",
            role="editor",
        )

        # Create publisher and assign editor
        self.publisher1 = Publisher.objects.create(name="Publisher 1")
        self.publisher1.editors.add(self.editor)

        # Publisher for negative tests
        self.publisher2 = Publisher.objects.create(name="Publisher 2")
        self.publisher2.editors.add(self.other_editor)

        # Articles
        self.article1 = Article.objects.create(
            title="Article 1",
            content="Content 1",
            is_approved=True,
            publisher=self.publisher1,
        )

        self.article2 = Article.objects.create(
            title="Article 2",
            content="Content 2",
            is_approved=True,
            publisher=self.publisher2,
        )

        # Newsletters
        self.newsletter1 = Newsletter.objects.create(
            title="Newsletter 1",
            is_independant=False,
            publisher=self.publisher1,
        )

        self.newsletter2 = Newsletter.objects.create(
            title="Newsletter 2",
            is_independant=False,
            publisher=self.publisher2,
        )

        # API Client login
        self.client = APIClient()
        self.client.login(username="editor1", password="pass1234")

    def test_all_articles_only_shows_editor_articles(self):
        url = reverse('news:editors_dashboard')
        response = self.client.get(url)
        self.assertContains(response, "Article 1")
        self.assertNotContains(response, "Article 2")

    def test_view_article_access(self):
        url = reverse('news:editors_view_article', args=[self.article1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article1.title)

    def test_view_article_denied(self):
        url = reverse('news:editors_view_article', args=[self.article2.pk])
        response = self.client.get(url)
        # Should redirect if editor does not manage publisher
        self.assertEqual(response.status_code, 302)

    def test_update_article_post(self):
        url = reverse('news:editors_update_article', args=[self.article1.pk])
        response = self.client.post(
            url,
            {
                "title": "Updated Title",
                "content": "Updated Content",
                "is_approved": True,
            },
        )
        self.assertRedirects(response, reverse('news:editors_dashboard'))
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.title, "Updated Title")

    def test_delete_article_post(self):
        url = reverse('news:editors_delete_article', args=[self.article1.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('news:editors_dashboard'))
        self.assertFalse(Article.objects.filter(pk=self.article1.pk).exists())

    def test_all_newsletters_only_shows_editor_newsletters(self):
        url = reverse('news:editors_news_dashboard')
        response = self.client.get(url)
        self.assertContains(response, "Newsletter 1")
        self.assertNotContains(response, "Newsletter 2")

    def test_view_newsletter_access(self):
        url = reverse(
            'news:editors_view_newsletter', args=[self.newsletter1.pk]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.newsletter1.title)

    def test_update_newsletter_post(self):
        url = reverse('news:editors_update_news', args=[self.newsletter1.pk])
        response = self.client.post(
            url,
            {
                "title": "Updated Newsletter",
                "articles": [self.article1.pk],  # include required M2M
            },
        )
        self.assertRedirects(response, reverse('news:editors_news_dashboard'))
        self.newsletter1.refresh_from_db()
        self.assertEqual(self.newsletter1.title, "Updated Newsletter")

    def test_delete_newsletter_post(self):
        url = reverse('news:editors_delete_news', args=[self.newsletter1.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('news:editors_news_dashboard'))
        self.assertFalse(
            Newsletter.objects.filter(pk=self.newsletter1.pk).exists()
        )


class PublisherViewsTests(TestCase):
    def setUp(self):
        # Create user and assign to manager_publishers group
        self.user = CustomUser.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="pass1234",
        )
        group, _ = Group.objects.get_or_create(name="Manage_Publishers")
        self.user.groups.add(group)
        self.user.save()

        # Log in client
        self.client.login(username="adminuser", password="pass1234")

        # Create a sample publisher
        self.publisher = Publisher.objects.create(name="Test Publisher")

    # ---------------- CREATE ----------------
    def test_create_publisher_get(self):
        response = self.client.get(reverse("news:admins_create_publisher"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_create_publisher_post_valid(self):
        response = self.client.post(
            reverse("news:admins_create_publisher"),
            {"name": "New Publisher", "description": "Test desc"},
        )
        self.assertRedirects(response, reverse("news:all_publishers"))
        self.assertTrue(
            Publisher.objects.filter(name="New Publisher").exists()
        )

    def test_create_publisher_post_duplicate_name(self):
        response = self.client.post(
            reverse("news:admins_create_publisher"),
            {"name": self.publisher.name, "description": "Some desc"},
        )
        self.assertContains(
            response, "Publisher with this Name already exists."
        )

    # ---------------- READ ----------------
    def test_read_publishers_list(self):
        response = self.client.get(reverse("news:all_publishers"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.publisher.name)

    def test_read_publishers_with_query(self):
        response = self.client.get(
            reverse("news:all_publishers"), {"q": "Test"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.publisher.name)

    # ---------------- DETAILS ----------------
    def test_publisher_details_existing(self):
        response = self.client.get(
            reverse("news:admins_publisher_details", args=[self.publisher.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.publisher.name)

    def test_publisher_details_nonexistent(self):
        response = self.client.get(
            reverse("news:admins_publisher_details", args=[999])
        )
        self.assertEqual(response.status_code, 404)

    # ---------------- UPDATE ----------------
    def test_update_publisher_get(self):
        response = self.client.get(
            reverse("news:admins_update_publisher", args=[self.publisher.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_update_publisher_post_valid(self):
        response = self.client.post(
            reverse("news:admins_update_publisher", args=[self.publisher.pk]),
            {"name": "Updated Publisher", "description": "Updated desc"},
        )
        self.assertRedirects(response, reverse("news:all_publishers"))
        self.publisher.refresh_from_db()
        self.assertEqual(self.publisher.name, "Updated Publisher")

    # ---------------- DELETE ----------------
    def test_delete_publisher_get(self):
        response = self.client.get(
            reverse("news:admins_delete_publisher", args=[self.publisher.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.publisher.name)

    def test_delete_publisher_post(self):
        response = self.client.post(
            reverse("news:admins_delete_publisher", args=[self.publisher.pk])
        )
        self.assertRedirects(response, reverse("news:all_publishers"))
        self.assertFalse(
            Publisher.objects.filter(pk=self.publisher.pk).exists()
        )


class JournalistViewsTests(TestCase):
    def setUp(self):
        # Create a journalist user
        self.journalist = CustomUser.objects.create_user(
            username="journalist1", password="password123"
        )
        journalist_group, _ = Group.objects.get_or_create(name="Journalist")
        self.journalist.groups.add(journalist_group)

        self.client = Client()
        self.client.login(username="journalist1", password="password123")

        # Sample publisher
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.publisher.journalists.add(self.journalist)

        # Sample article
        self.article = Article.objects.create(
            title="Test Article",
            content="Test Content",
            made_by_journalist=self.journalist,
            is_approved=True,
            is_independant=True,
        )

        # Sample newsletter
        self.newsletter = Newsletter.objects.create(
            title="Test Newsletter",
            journalist=self.journalist,
            is_independant=True,
        )
        self.newsletter.articles.add(self.article)

    # ------------------ ARTICLES ------------------ #
    def test_create_article_get(self):
        response = self.client.get(reverse("news:journalists_create_article"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_create_article_post(self):
        data = {
            "title": "New Article",
            "content": "New content",
            "is_independant": True, 
            "publisher": "",  # empty for independant
            "is_approved": True,
        }
        response = self.client.post(
            reverse("news:journalists_create_article"), data
        )
        self.assertEqual(
            Article.objects.filter(title="New Article").count(), 1
        )
        self.assertRedirects(response, reverse("news:journalists_dashboard"))

    def test_read_articles(self):
        response = self.client.get(reverse("news:journalists_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_view_article(self):
        response = self.client.get(
            reverse("news:journalists_view_article", args=[self.article.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_update_article_post(self):
        data = {
            "title": "Updated Title",
            "content": "Updated content",
            "is_independant": True,
            "publisher": "",  # empty for independant
            "is_approved": True,
        }
        response = self.client.post(
            reverse("news:journalists_update_article", args=[self.article.pk]),
            data,
        )
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Updated Title")
        self.assertRedirects(response, reverse("news:journalists_dashboard"))

    def test_delete_article_post(self):
        response = self.client.post(
            reverse("news:journalists_delete_article", args=[self.article.pk])
        )
        self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())
        self.assertRedirects(response, reverse("news:journalists_dashboard"))

    # ------------------ NEWSLETTERS ------------------ #
    def test_create_newsletter_get(self):
        response = self.client.get(
            reverse("news:journalists_create_newsletter")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    def test_create_newsletter_post(self):
        data = {
            "title": "New Newsletter",
            "articles": [self.article.pk],
            "is_independant": True,
            "publisher": "",  # empty for independant
        }
        response = self.client.post(
            reverse("news:journalists_create_newsletter"), data
        )
        self.assertEqual(
            Newsletter.objects.filter(title="New Newsletter").count(), 1
        )
        self.assertRedirects(
            response, reverse("news:journalists_news_dashboard")
        )

    def test_newsletter_dashboard(self):
        response = self.client.get(reverse("news:journalists_news_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.newsletter.title)

    def test_view_newsletter(self):
        response = self.client.get(
            reverse(
                "news:journalists_view_newsletter", args=[self.newsletter.pk]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.newsletter.title)

    def test_update_newsletter_post(self):
        data = {
            "title": "Updated Newsletter",
            "articles": [self.article.pk],
            "is_independant": True,
            "publisher": "",  # empty for independant
        }
        response = self.client.post(
            reverse(
                "news:journalists_update_newsletter", args=[self.newsletter.pk]
            ),
            data,
        )
        self.newsletter.refresh_from_db()
        self.assertEqual(self.newsletter.title, "Updated Newsletter")
        self.assertRedirects(
            response, reverse("news:journalists_news_dashboard")
        )

    def test_delete_newsletter_post(self):
        response = self.client.post(
            reverse("news:journalists_delete_news", args=[self.newsletter.pk])
        )
        self.assertFalse(
            Newsletter.objects.filter(pk=self.newsletter.pk).exists()
        )
        self.assertRedirects(
            response, reverse("news:journalists_news_dashboard")
        )
