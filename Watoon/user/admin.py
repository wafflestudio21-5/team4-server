from django.contrib import admin

from .models import User

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nickname',
        'email',
    )

    list_display_links = (
        'nickname',
        'email',
    )

admin.site.register(User, UserAdmin)