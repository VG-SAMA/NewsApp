from django.test import TestCase
from accounts.models import CustomUser
from news.models import Publisher
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserSaveTest(TestCase):
    def test_m2m_clear_for_journalist(self):
        pub = Publisher.objects.create(name="TestPub", description="desc")
        user = CustomUser.objects.create_user(
            username="j1",
            email="j1@test.com",
            password="pass",
            role="journalist",
        )

        # add M2M manually
        user.reader_publisher_subscriptions.add(pub)
        user.reader_journalist_subscriptions.add(user)

        user.save()  # triggers M2M clear

        self.assertEqual(user.reader_publisher_subscriptions.count(), 0)
        self.assertEqual(user.reader_journalist_subscriptions.count(), 0)


class UserAuthTests(TestCase):

    def setUp(self):
        # Create a sample user for login tests
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="securepass123",
            role="reader",
        )

    def test_user_registration(self):
        """
        Test that a new user can register successfully
        """
        response = self.client.post(
            reverse("accounts:register"),
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
                "role": "reader",
            },
        )
        self.assertEqual(response.status_code, 302)  # redirects after success
        user_exists = User.objects.filter(username="newuser").exists()
        self.assertTrue(user_exists)

    def test_user_login(self):
        """
        Test that an existing user can log in successfully
        """
        response = self.client.post(
            reverse("accounts:login"),
            data={"username": "testuser", "password": "securepass123"},
        )
        self.assertEqual(
            response.status_code, 302
        )  # should redirect after login
        # check if the user is authenticated
        response = self.client.get(reverse("news:readers_dashboard"))
        self.assertEqual(response.context["user"].is_authenticated, True)

    def test_failed_login(self):
        """
        Test that login fails with incorrect credentials
        """
        response = self.client.post(
            reverse("accounts:login"),
            data={"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)  # login page re-rendered
        self.assertContains(response, "Invalid username or password")
