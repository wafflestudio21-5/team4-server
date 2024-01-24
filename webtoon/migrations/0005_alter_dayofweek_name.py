# Generated by Django 4.2.7 on 2024-01-23 07:46

from django.db import migrations, models
import webtoon.validators


class Migration(migrations.Migration):

    dependencies = [
        ('webtoon', '0004_alter_userprofile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dayofweek',
            name='name',
            field=models.CharField(max_length=10, unique=True, validators=[webtoon.validators.isDayName]),
        ),
    ]
