# Generated by Django 4.0.4 on 2022-05-30 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
    ]