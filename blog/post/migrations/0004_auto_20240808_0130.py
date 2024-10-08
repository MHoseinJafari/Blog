# Generated by Django 3.2.25 on 2024-08-08 01:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("post", "0003_auto_20240807_1741"),
    ]

    operations = [
        migrations.RenameField(
            model_name="post",
            old_name="number_of_voters",
            new_name="voters",
        ),
        migrations.RemoveField(
            model_name="post",
            name="temp_rate",
        ),
        migrations.RemoveField(
            model_name="vote",
            name="temp_vote",
        ),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="post",
                related_query_name="post",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
