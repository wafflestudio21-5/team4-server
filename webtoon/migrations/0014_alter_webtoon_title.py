# Generated by Django 4.2.7 on 2024-02-02 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webtoon', '0013_alter_episode_thumbnail_alter_webtoon_titleimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webtoon',
            name='title',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
