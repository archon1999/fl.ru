# Generated by Django 3.2 on 2021-09-21 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='bot_state',
            field=models.IntegerField(blank=True, choices=[(1, 'Edit Min Budget')], null=True),
        ),
    ]
