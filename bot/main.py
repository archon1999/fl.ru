import config

import telebot

from backend.models import BotUser
from backend.templates import Keys

from bot import commands, projects, settings
from bot.call_types import CallTypes


bot = telebot.TeleBot(
    token=config.TOKEN,
    num_threads=3,
    parse_mode='HTML',
)

keyboard_handlers = {
    Keys.MENU: commands.menu_command_handler,
}


message_handlers = {
    '/start': commands.start_command_handler,
    '/menu': commands.menu_command_handler,
}


@bot.message_handler(content_types=['text'])
def message_handler(message):
    chat_id = message.chat.id

    if message.text in Keys.CANCEL.getall():
        commands.cancel_command_handler(bot, message)
        return

    user, _ = BotUser.users.get_or_create(chat_id=chat_id)
    if (state := user.state):
        if state == BotUser.State.EDIT_BUDGET_MIN:
            settings.filter_budget_min_message_handler(bot, message)

        if state == BotUser.State.EDIT_BUDGET_MAX:
            settings.filter_budget_max_message_handler(bot, message)

        return

    for text, message_handler in message_handlers.items():
        if message.text in text:
            message_handler(bot, message)
            break

    for key, message_handler in keyboard_handlers.items():
        if message.text in key.getall():
            message_handler(bot, message)
            break

    bot.delete_message(chat_id, message.id)


callback_query_handlers = {
    CallTypes.Nothing: lambda _, __: True,
    CallTypes.Menu: commands.menu_call_handler,
    CallTypes.Back: commands.back_call_handler,

    CallTypes.Settings: settings.settings_call_handler,
    CallTypes.FilterActive: settings.filter_active_call_handler,
    CallTypes.FilterSafeDeal: settings.filter_safe_deal_call_handler,
    CallTypes.FilterBudgetMin: settings.filter_budget_min_call_handler,
    CallTypes.FilterBudgetMax: settings.filter_budget_max_call_handler,
    CallTypes.FilterChapters: settings.filter_chapters_call_handler,
    CallTypes.FilterChapter: settings.filter_chapter_call_handler,
    CallTypes.FilterChapterSelectAll:
        settings.filter_chapter_select_all_call_handler,
    CallTypes.FilterChapterReset: settings. filter_chapter_reset_call_handler,    
}


@bot.callback_query_handler(func=lambda _: True)
def callback_query_handler(call):
    call_type = CallTypes.parse_data(call.data)
    for CallType, query_handler in callback_query_handlers.items():
        if call_type.__class__.__name__ == CallType.__name__:
            query_handler(bot, call)
            break


if __name__ == "__main__":
    # bot.polling()
    bot.infinity_polling()
