# myapp/tests/test_views.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from ..models import Post


class PostModelViewSetTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpassword"
        )

        self.post = Post.objects.create(
            title="Test Post",
            content="Content for test post",
            author=self.user,
            visible=True,
        )

        self.post_list_url = reverse("post:post-list")
        self.post_detail_url = reverse("post:post-detail", args=[self.post.id])

    def test_get_posts_as_anonymous_user(self):
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Post")

    def test_create_post_as_authenticated_user(self):
        self.client.login(username="testuser", password="testpassword")
        data = {
            "title": "New Post",
            "content": "Content of new post",
            "visible": True,
        }
        response = self.client.post(self.post_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(
            Post.objects.get(id=response.data["id"]).title, "New Post"
        )

    def test_create_post_as_anonymous_user(self):
        data = {
            "title": "Another Post",
            "content": "Content of another post",
            "visible": True,
        }
        response = self.client.post(self.post_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post_as_owner(self):
        self.client.login(username="testuser", password="testpassword")
        data = {
            "title": "Updated Post",
            "content": "Updated content",
            "visible": True,
        }
        response = self.client.put(self.post_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Post")

    def test_update_post_as_non_owner(self):
        self.client.login(username="admin", password="adminpassword")
        data = {
            "title": "Updated by admin",
            "content": "Updated content by admin",
            "visible": True,
        }
        response = self.client.put(self.post_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_as_owner(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.delete(self.post_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_post_as_non_owner(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.delete(self.post_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VoteApiViewTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.anonymous_client = self.client
        self.authenticated_client = self.client
        self.authenticated_client.login(
            username="testuser", password="testpassword"
        )

        self.post = Post.objects.create(
            title="Test Post", content="Content for test post", visible=True
        )

        self.vote_url = reverse("post:vote")

    def test_submit_vote_as_authenticated_user(self):
        data = {"vote": 1, "post": self.post.id}
        response = self.authenticated_client.post(
            self.vote_url, data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"],
            "Your vote has been successfully submitted",
        )

        self.post.refresh_from_db()
        self.assertEqual(
            self.post.vote.count(), 1
        )  # Assuming there's a `vote_count` field or similar.

    def test_submit_vote_with_invalid_data(self):
        self.authenticated_client.login(
            username="testuser", password="testpassword"
        )

        data = {"vote": "invalid", "post": self.post.id}
        response = self.authenticated_client.post(
            self.vote_url, data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("vote", response.data)

        data = {"vote": 1}
        response = self.authenticated_client.post(
            self.vote_url, data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("post", response.data)
