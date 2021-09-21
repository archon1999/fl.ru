import telebot
from django.db.models.query import QuerySet

from backend.models import BotUser, BotUserFilter, Project, Chapter
from backend.templates import Keys

from bot.call_types import CallTypes


def get_projects_by_chapters(chapters: QuerySet[Chapter]):
    result = []
    for chapter in chapters:
        projects = Project.projects.filter(chapters__in=chapter)
        if not result:
            result = projects
        else:
            result |= projects

    return projects


def projects_call_handler(bot: telebot.TeleBot, call):
    call_type = CallTypes.parse_data(call.data)
    page_number = call_type.page
