# Generated by Django 3.2.25 on 2024-08-08 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0004_auto_20240808_0130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='processed',
        ),
        migrations.AddField(
            model_name='post',
            name='temp_rate',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='temp_voters',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
