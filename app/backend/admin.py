from django.contrib import admin

from backend.models import (BotUser, BotUserFilter, Chapter, Project,
                            TaskManager, Template)


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_id', 'full_name', 'created']


@admin.register(BotUserFilter)
class BotUserFilterAdmin(admin.ModelAdmin):
    list_display = ['user', 'budget_min', 'budget_max', 'only_safe_deal',
                    'only_without_executor']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'budget', 'deadline', 'published']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(TaskManager)
class TaskManagerAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'project']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'title']
