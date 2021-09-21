import telebot
from telebot import types

from backend.templates import Messages, Keys
from backend.models import BotUser

from bot import utils
from bot.call_types import CallTypes


def start_command_handler(bot: telebot.TeleBot, message):
    menu_command_handler(bot, message)


def menu_command_handler(bot: telebot.TeleBot, message):
    chat_id = message.chat.id
    projects_button = utils.make_inline_button(
        text=Keys.PROJECTS.text,
        CallType=CallTypes.ProjectsPage,
        page=1,
    )
    settings_button = utils.make_inline_button(
        text=Keys.SETTINGS.text,
        CallType=CallTypes.Settings,
    )
    menu_keyboard = types.InlineKeyboardMarkup()
    menu_keyboard.add(projects_button, settings_button)

    if hasattr(message, 'called'):
        text = utils.text_to_fat(Keys.MENU.text)
        bot.edit_message_text(
            chat_id=chat_id,
            text=text,
            message_id=message.id,
            reply_markup=menu_keyboard)
    else:
        text = utils.text_to_fat(Keys.MENU.text)
        bot.send_message(chat_id, text,
                         reply_markup=menu_keyboard)


def menu_call_handler(bot: telebot.TeleBot, call):
    call.message.called = True
    menu_command_handler(bot, call.message)


def back_call_handler(bot: telebot.TeleBot, call):
    call.message.called = True
    menu_command_handler(bot, call.message)


def cancel_command_handler(bot: telebot.TeleBot, message):
    chat_id = message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user.state = None
    user.save()

    text = Messages.CANCELED.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(Keys.MENU.text)
    bot.send_message(chat_id, text,
                     reply_markup=keyboard)

    menu_command_handler(bot, message)
