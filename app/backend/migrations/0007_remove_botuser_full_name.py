# Generated by Django 3.2 on 2021-09-21 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_botuser_bot_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='full_name',
        ),
    ]