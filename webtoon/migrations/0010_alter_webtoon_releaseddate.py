# Generated by Django 4.2.7 on 2024-02-02 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webtoon', '0009_alter_episodeimage_episode_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webtoon',
            name='releasedDate',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
