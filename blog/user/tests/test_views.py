# tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.exceptions import NotAcceptable
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Profile
from ..serializers import RegistrationSerializer
from ..views import Signup


class SignupViewTest(TestCase):

    def setUp(self):
        """Set up the API client."""
        self.client = APIClient()
        self.url = "http://localhost:8088/v1/user/signup/"

    def test_successful_signup(self):
        """Test a successful signup request."""
        data = {
            "username": "testuser",
            "password": "testpassword123",
            "new_pass": "testpassword123",
            "email": "testuser@example.com",
            "first_name": "fill",
            "last_name": "colson",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if profile is created
        user = User.objects.get(username="testuser")
        self.assertTrue(Profile.objects.filter(user=user).exists())

        # Check if tokens are present in response
        response_data = response.json()
        self.assertIn("tokens", response_data)
        self.assertIn("refresh", response_data["tokens"])
        self.assertIn("access", response_data["tokens"])

        # Validate the refresh token
        refresh_token = response_data["tokens"]["refresh"]
        token = RefreshToken(refresh_token)
        self.assertEqual(str(token), refresh_token)

    def test_signup_with_existing_username(self):
        """Test signup with an existing username."""
        User.objects.create_user(
            username="testuser", password="testpassword123"
        )
        data = {
            "username": "testuser",
            "password": "testpassword123",
            "new_pass": "short",
            "email": "testuser@example.com",
            "first_name": "fill",
            "last_name": "colson",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_signup_data(self):
        """Test signup with invalid data."""
        data = {
            "username": "",  # Empty username
            "password": "short",  # Invalid password
            "new_pass": "short",
            "email": "invalid-email",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(TestCase):

    def setUp(self):
        """Set up the API client and create a test user."""
        self.client = APIClient()
        self.url = "http://localhost:8088/v1/user/login/"
        self.username = "testuser"
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

    def test_successful_login(self):
        """Test a successful login request."""
        data = {"username": self.username, "password": self.password}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if tokens are present in response
        response_data = response.json()
        self.assertIn("tokens", response_data)
        self.assertIn("refresh", response_data["tokens"])
        self.assertIn("access", response_data["tokens"])

        # Validate the refresh token
        refresh_token = response_data["tokens"]["refresh"]
        token = RefreshToken(refresh_token)
        self.assertEqual(str(token), refresh_token)

    def test_login_with_invalid_password(self):
        """Test login with an incorrect password."""
        data = {"username": self.username, "password": "wrongpassword"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_invalid_username(self):
        """Test login with a non-existent username."""
        data = {"username": "nonexistentuser", "password": self.password}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_missing_fields(self):
        """Test login with missing fields."""
        data = {"username": self.username}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_fields(self):
        """Test login with empty fields."""
        data = {"username": "", "password": ""}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
