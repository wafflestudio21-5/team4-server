from django.contrib import admin

from .models import UserProfile, DayOfWeek, Webtoon, Episode, Comment, Tag
# Register your models here.


class TagInline(admin.StackedInline):
    model = Tag.webtoons.through
    verbose_name = 'Tag'
    verbose_name_plural = 'Tags'


class WebtoonAdmin(admin.ModelAdmin):
    inlines = (
        TagInline,
    )


admin.site.register(UserProfile)
admin.site.register(DayOfWeek)
admin.site.register(Webtoon, WebtoonAdmin)
admin.site.register(Episode)
admin.site.register(Comment)
admin.site.register(Tag)