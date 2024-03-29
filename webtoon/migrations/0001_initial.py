# Generated by Django 4.2.7 on 2024-01-29 11:23

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import webtoon.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayOfWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True, validators=[webtoon.validators.isDayName])),
            ],
        ),
        migrations.CreateModel(
            name='Webtoon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('titleImage', models.CharField(max_length=50, null=True)),
                ('description', models.CharField(max_length=200)),
                ('isFinished', models.BooleanField(default=False)),
                ('totalRating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('releasedDate', models.DateField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploadedWebtoons', to=settings.AUTH_USER_MODEL)),
                ('subscribers', models.ManyToManyField(blank=True, related_name='subscribingWebtoons', to=settings.AUTH_USER_MODEL)),
                ('uploadDays', models.ManyToManyField(related_name='webtoons', to='webtoon.dayofweek')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('introduction', models.CharField(blank=True, max_length=200, null=True)),
                ('isAuthor', models.BooleanField(default=False)),
                ('subscribers', models.ManyToManyField(blank=True, related_name='subscribingAuthors', to='webtoon.userprofile')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('content', models.CharField(max_length=20, primary_key=True, serialize=False, unique=True)),
                ('webtoons', models.ManyToManyField(blank=True, related_name='tags', to='webtoon.webtoon')),
            ],
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('episodeNumber', models.IntegerField()),
                ('totalRating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('releasedDate', models.DateField(auto_now_add=True)),
                ('likedBy', models.PositiveIntegerField(default=0)),
                ('webtoon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='webtoon.webtoon')),
            ],
            options={
                'unique_together': {('webtoon', 'episodeNumber')},
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=300)),
                ('dtCreated', models.DateTimeField(auto_now_add=True)),
                ('dtUpdated', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('likedBy', models.PositiveIntegerField(default=0)),
                ('dislikedBy', models.PositiveIntegerField(default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('createdBy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('createdBy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to=settings.AUTH_USER_MODEL)),
                ('ratingOn', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='webtoon.episode')),
            ],
            options={
                'unique_together': {('createdBy', 'ratingOn')},
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isLike', models.BooleanField()),
                ('isDislike', models.BooleanField()),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('createdBy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('createdBy', 'content_type', 'object_id')},
            },
        ),
    ]
