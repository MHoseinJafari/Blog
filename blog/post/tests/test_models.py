from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Post, Vote
from django.db import transaction

from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotAcceptable
from django.db import IntegrityError


class PostModelTests(TestCase):

    def setUp(self):
        """
        Create a user and a post for testing.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.post = Post.objects.create(
            title="Test Post",
            content="this is a test post content",
            author=self.user,
            visible=True,
        )

    def test_create_post(self):
        """
        Test the creation of a Post object.
        """
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.content, "this is a test post content")
        self.assertEqual(self.post.author, self.user)
        self.assertTrue(self.post.visible)
        self.assertEqual(self.post.rate, 0)
        self.assertEqual(self.post.rate, 0)
        self.assertEqual(self.post.voters, 0)
        self.assertIsNotNone(self.post.created_date)

    def test_str_method(self):
        """
        Test the __str__ method of the Post model.
        """
        self.assertEqual(str(self.post), "Test Post")

    def test_update_post(self):
        """
        Test updating Post fields.
        """
        self.post.title = "Updated Post Title"
        self.post.save()
        updated_post = Post.objects.get(id=self.post.id)
        self.assertEqual(updated_post.title, "Updated Post Title")

    def test_author_foreign_key(self):
        """
        Test the ForeignKey relationship between Post and User.
        """
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post, self.user.post.all()[0])

    def test_post_creation_performance(self):
        """
        Test the performance of creating a large number of posts.
        """
        import time

        start_time = time.time()
        for i in range(1000):
            Post.objects.create(
                title=f"Test Post {i}",
                content="Content for performance test.",
                author=self.user,
                visible=True,
            )
        duration = time.time() - start_time
        self.assertLess(duration, 2)

    def test_post_created_date_auto_now_add(self):
        """
        Test if created_date field is automatically set to the current date and time.
        """
        from django.utils import timezone

        post = Post.objects.create(
            title="New Post",
            content="Content for new post.",
            author=self.user,
            visible=True,
        )
        self.assertAlmostEqual(
            post.created_date,
            timezone.now(),
            delta=timezone.timedelta(seconds=1),
        )


class VoteModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post content.",
            author=self.user,
            visible=True,
        )

    def test_create_vote(self):
        vote = Vote.objects.create(
            user=self.user,
            post=self.post,
            vote=5,
        )
        self.assertEqual(vote.user, self.user)
        self.assertEqual(vote.post, self.post)
        self.assertEqual(vote.vote, 5)

    def test_default_values(self):
        vote = Vote.objects.create(user=self.user, post=self.post)
        self.assertEqual(vote.vote, 0)

    def test_str_method(self):
        vote = Vote.objects.create(user=self.user, post=self.post, vote=3)
        self.assertEqual(
            str(vote),
            f"Vote {vote.id} by {self.user.username} on {self.post.title}",
        )


class VoteSubmitTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username="testuser")
        self.post = Post.objects.create(title="Test Post", rate=0, voters=0)

    def test_add_vote(self):
        self.post.vote_submit(user=self.user, amount=5)
        self.assertEqual(self.post.temp_voters, 1)
        self.assertEqual(self.post.temp_rate, 5)
        self.assertTrue(
            Vote.objects.filter(post=self.post, user=self.user).exists()
        )

    def test_update_vote(self):
        self.post.vote_submit(user=self.user, amount=3)
        # Update vote
        self.post.vote_submit(user=self.user, amount=2)
        self.assertEqual(self.post.temp_voters, 1)
        self.assertEqual(self.post.temp_rate, 2)

    def test_multiple_votes(self):
        new_user = User.objects.create(username="newuser")
        self.post.vote_submit(user=self.user, amount=3)
        self.post.vote_submit(user=new_user, amount=5)
        self.assertEqual(self.post.temp_voters, 2)
        self.assertEqual(self.post.temp_rate, (5 + 3) / 2)
        self.assertTrue(
            Vote.objects.filter(post=self.post, user=self.user).exists()
        )
        self.assertTrue(
            Vote.objects.filter(post=self.post, user=new_user).exists()
        )

    def test_invalid_vote_amount(self):
        with self.assertRaises(NotAcceptable):
            self.post.vote_submit(user=self.user, amount=7)

    def test_no_votes(self):
        self.post.vote_submit(user=self.user, amount=0)
        self.assertEqual(self.post.temp_voters, 1)
        self.assertEqual(self.post.temp_rate, 0)
        vote = Vote.objects.get(post=self.post, user=self.user)
        self.assertEqual(vote.vote, 0)

    def test_negative_vote_amount(self):
        with self.assertRaises(NotAcceptable):
            self.post.vote_submit(user=self.user, amount=-1)

    def test_transactional_vote_amount(self):
        with self.assertRaises(NotAcceptable):
            with self.assertRaises(IntegrityError):
                with transaction.atomic():
                    self.post.vote_submit(user=self.user, amount=7)
                    self.assertEqual(self.post.temp_voters, 0)
                    self.assertEqual(self.post.temp_rate, 0)

    def test_update_vote_recalculate_average(self):
        user2 = User.objects.create(username="testuser2")
        self.post.vote_submit(user=self.user, amount=4)
        self.post.vote_submit(user=user2, amount=2)
        self.assertEqual(self.post.temp_voters, 2)
        self.assertEqual(self.post.temp_rate, (4 + 2) / 2)
        self.post.vote_submit(user=self.user, amount=5)
        self.assertEqual(self.post.temp_voters, 2)
        self.assertEqual(self.post.temp_rate, (5 + 2) / 2)
