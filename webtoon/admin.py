from django.contrib import admin

from .models import UserProfile, DayOfWeek, Webtoon, Episode, Comment, Tag, Rating, Like
# Register your models here.


class TagInline(admin.StackedInline):
    model = Tag.webtoons.through
    verbose_name = 'Tag'
    verbose_name_plural = 'Tags'


class WebtoonInline(admin.StackedInline):
    model = Webtoon.uploadDays.through
    verbose_name = 'Webtoon'
    verbose_name_plural = 'Webtoons'


class WebtoonAdmin(admin.ModelAdmin):
    inlines = (
        TagInline,
    )


class DayOfWeekAdmin(admin.ModelAdmin):
    inlines = (
        WebtoonInline,
    )


admin.site.register(UserProfile)
admin.site.register(DayOfWeek, DayOfWeekAdmin)
admin.site.register(Webtoon, WebtoonAdmin)
admin.site.register(Episode)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Rating)
admin.site.register(Like)