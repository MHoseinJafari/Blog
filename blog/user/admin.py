from django.contrib import admin
from . import models


@admin.register(models.Profile)
class Profile(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "fullname",
    )
    search_fields = (
        "id",
        "first_name",
        "last_name",
    )
