from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
from rest_framework.exceptions import NotAcceptable
from django.db import transaction




class Post(models.Model):
    title = models.CharField(max_length=30, default="Post title")
    content = models.TextField(default="Post content")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='post', related_query_name='post')
    visible = models.BooleanField(default=False)
    rate = models.FloatField(default=0)
    temp_rate = models.FloatField(default=0)
    voters = models.IntegerField(default=0)
    temp_voters = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return self.title
    
    
    def vote_submit(self, user: User, amount: int) -> None:
        if amount in range(6):
            with transaction.atomic():
                # Calculate previous total votes if there are any voters
                previous_total_vote = self.temp_rate * self.temp_voters
                old_vote = Vote.objects.select_for_update().filter(post=self, user=user).first()
                if old_vote:
                    # Update the total rating by removing the old vote and adding the new one
                    previous_total_vote -= old_vote.vote
                    # Update the existing vote with the new amount
                    old_vote.vote = amount
                    old_vote.save()
                else:
                    # Increment the number of voters and create a new vote
                    self.temp_voters += 1
                    Vote.objects.create(post=self, user=user, vote=amount)
                # Calculate the new total rating with the new vote
                new_total_rating = previous_total_vote + amount
                # Update the average rating based on the new total rating
                if self.temp_voters > 0:
                    self.temp_rate = new_total_rating / self.temp_voters
                else:
                    self.temp_rate = 0

                # Save the changes to the model
                self.save()
        
        else:
            raise NotAcceptable({"detail": "invalid vote"})


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="vote")
    vote = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Vote {self.id} by {self.user.username} on {self.post.title}"


