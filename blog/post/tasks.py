from celery import shared_task
from .models import Post


@shared_task
def process_scheduled_votes():
    posts = Post.objects.filter(visible=True)

    for post in posts:
        post.refresh_from_db()
        post.rate = post.temp_rate
        post.voters = post.temp_voters
        post.save()
