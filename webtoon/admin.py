from django.contrib import admin

from .models import UserProfile, DayOfWeek, Webtoon, Episode, Comment, Tag
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(DayOfWeek)
admin.site.register(Webtoon)
admin.site.register(Episode)
admin.site.register(Comment)
admin.site.register(Tag)