# Generated by Django 4.2.7 on 2024-02-02 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webtoon', '0010_alter_webtoon_releaseddate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='releasedDate',
            field=models.DateTimeField(),
        ),
    ]
