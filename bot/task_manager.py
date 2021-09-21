import time
import traceback

import telebot

import config
import utils

from backend.templates import Messages
from backend.models import TaskManager, Project, BotUser


LOGO_IMAGE_PATH = '../parser/logo.jpg'


def get_project_info(project: Project):
    return Messages.PROJECT.text.format(
            article=project.article,
            title=project.title,
            safe_deal_info=project.get_safe_deal_info(),
            budget_info=project.get_budget_info(),
            deadline_info=project.get_deadline_info(),
            description=project.get_description(),
            chapters_info=project.get_chapters_info(),
            url=project.url,
            published=utils.datetime_to_utc5_str(project.published),
        )


def send_project(bot: telebot.TeleBot, project: Project):
    for user in BotUser.users.all():
        if user.filter.is_valid_project(project) and user.filter.active:
            try:
                project_info = get_project_info(project)
                with open(LOGO_IMAGE_PATH, 'rb') as photo:
                    bot.send_photo(
                        chat_id=user.chat_id,
                        photo=photo,
                        caption=project_info,
                    )
            except Exception:
                pass


def main():
    bot = telebot.TeleBot(
        config.TOKEN,
        parse_mode='HTML',
        num_threads=1,
    )
    while True:
        if (task := TaskManager.unfulfilled.last()) is None:
            time.sleep(5)
            continue

        try:
            if task.type == TaskManager.Type.NEW_PROJECT:
                project: Project = task.project
                send_project(bot, project)
            task.done = True
        except Exception:
            print(traceback.format_exc())   
        finally:
            task.save()
            time.sleep(5)


if __name__ == '__main__':
    main()
