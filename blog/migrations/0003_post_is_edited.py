# Generated by Django 5.1.3 on 2024-12-08 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_post_token_alter_post_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
    ]
