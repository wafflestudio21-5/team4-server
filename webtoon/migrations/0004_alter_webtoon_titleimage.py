# Generated by Django 4.2.7 on 2024-02-01 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webtoon', '0003_alter_webtoon_uploaddays'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webtoon',
            name='titleImage',
            field=models.ImageField(default='default', upload_to='titleImage/'),
        ),
    ]
