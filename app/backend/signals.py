from django.db.models.signals import post_save
from django.dispatch import receiver


from backend.models import BotUser, BotUserFilter, Project, TaskManager


@receiver(post_save, sender=BotUser)
def bot_user_post_save_handler(sender, instance, created, **kwargs):
    if created:
        BotUserFilter.objects.create(user=instance)


@receiver(post_save, sender=Project)
def project_post_save_handler(sender, instance, created, **kwargs):
    if created:
        TaskManager.tasks.create(
            type=TaskManager.Type.NEW_PROJECT,
            project=instance,
        )
