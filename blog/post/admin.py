from django.contrib import admin
from . import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "rate", "visible", "created_date")
    list_filter = ("visible",)
    search_fields = ("id",)


@admin.register(models.Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "post",
        "vote",
    )
    list_filter = ("user",)
