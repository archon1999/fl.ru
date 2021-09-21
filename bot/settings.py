import telebot
from telebot import types

from backend.models import BotUser, BotUserFilter, Chapter
from backend.templates import Keys, Messages, Smiles

from bot.call_types import CallTypes
from bot import utils


def get_on_off_info(flag: bool):
    return [Keys.OFF.text, Keys.ON][flag]


def get_active_info(user_filter: BotUserFilter):
    return f'{Keys.NOTIFICATIONS}:  {get_on_off_info(user_filter.active)}'


def get_budget_min_info(user_filter: BotUserFilter):
    budget = user_filter.budget_min
    return f'{Keys.BUDGET_MIN}:  {budget if budget else Keys.NOT_INDICATED}'


def get_budget_max_info(user_filter: BotUserFilter):
    budget = user_filter.budget_max
    return f'{Keys.BUDGET_MAX}:  {budget if budget else Keys.NOT_INDICATED}'


def get_safe_deal_info(user_filter: BotUserFilter):
    return f'{Keys.SAFE_DEAL}:  {get_on_off_info(user_filter.safe_deal)}'


def get_keywords_info(user_filter: BotUserFilter):
    keywords = user_filter.keywords
    return f'{Keys.KEYWORDS}:  {keywords if keywords else Keys.NOT_INDICATED}'


def settings_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)

    active_button = utils.make_inline_button(
        text=get_active_info(user.filter),
        CallType=CallTypes.FilterActive,
    )
    chapters_button = utils.make_inline_button(
        text=Keys.CHAPTERS.text,
        CallType=CallTypes.FilterChapters,
    )
    safe_deal_button = utils.make_inline_button(
        text=get_safe_deal_info(user.filter),
        CallType=CallTypes.FilterSafeDeal,
    )
    budget_min_button = utils.make_inline_button(
        text=get_budget_min_info(user.filter),
        CallType=CallTypes.FilterBudgetMin,
    )
    budget_max_button = utils.make_inline_button(
        text=get_budget_max_info(user.filter),
        CallType=CallTypes.FilterBudgetMax,
    )
    keywords_button = utils.make_inline_button(
        text=get_keywords_info(user.filter),
        CallType=CallTypes.FilterKeywords,
    )
    back_button = utils.make_inline_button(
        text=Keys.BACK.text,
        CallType=CallTypes.Back,
    )
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(active_button)
    keyboard.add(chapters_button)
    keyboard.add(safe_deal_button)
    keyboard.add(budget_min_button)
    keyboard.add(budget_max_button)
    keyboard.add(keywords_button)
    keyboard.add(back_button)
    text = utils.text_to_fat(Keys.SETTINGS.text)
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


def filter_active_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user.filter.active ^= True
    user.filter.save()
    settings_call_handler(bot, call)


def filter_safe_deal_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user.filter.safe_deal ^= True
    user.filter.save()
    settings_call_handler(bot, call)


def filter_budget_min_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user.state = BotUser.State.EDIT_BUDGET_MIN
    user.save()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(Keys.CANCEL.text)
    text = Messages.ENTER.text
    bot.send_message(chat_id, text,
                     reply_markup=keyboard)


def filter_budget_min_message_handler(bot: telebot.TeleBot, message):
    chat_id = message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    try:
        budget = int(message.text)
        if budget < 0:
            raise ValueError()
    except Exception:
        text = Messages.FILTER_BUDGET_INCORRECT_INPUT.text
        bot.send_message(chat_id, text)
    else:
        user.filter.budget_min = budget
        user.filter.save()
        user.state = None
        user.save()
        text = Messages.SAVED.text
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(Keys.MENU.text)
        bot.send_message(chat_id, text,
                         reply_markup=keyboard)


def filter_budget_max_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user.state = BotUser.State.EDIT_BUDGET_MAX
    user.save()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(Keys.CANCEL.text)
    text = Messages.ENTER.text
    bot.send_message(chat_id, text,
                     reply_markup=keyboard)


def filter_budget_max_message_handler(bot: telebot.TeleBot, message):
    chat_id = message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    try:
        budget = int(message.text)
        if budget < 0:
            raise ValueError()
    except Exception:
        text = Messages.FILTER_BUDGET_INCORRECT_INPUT.text
        bot.send_message(chat_id, text)
    else:
        user.filter.budget_max = budget
        user.filter.save()
        user.state = None
        user.save()
        text = Messages.SAVED.text
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(Keys.MENU.text)
        bot.send_message(chat_id, text,
                         reply_markup=keyboard)


def filter_chapters_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user_chapters = user.filter.chapters

    chapters = Chapter.chapters.filter(parent=None)
    keyboard = types.InlineKeyboardMarkup()
    for chapter in chapters:
        chapter_selected = user_chapters.filter(parent=chapter).exists()
        smiles = [Smiles.OFF.text, Smiles.ON.text]
        text = f'{chapter.name} {smiles[chapter_selected]}'
        chapter_button = utils.make_inline_button(
            text=text,
            CallType=CallTypes.FilterChapter,
            chapter_id=chapter.id,
        )
        keyboard.add(chapter_button)

    reset_button = utils.make_inline_button(
        text=Keys.RESET.text,
        CallType=CallTypes.FilterChapterReset,
        chapter_id=0,
    )
    back_button = utils.make_inline_button(
        text=Keys.SETTINGS.text,
        CallType=CallTypes.Settings,
    )
    keyboard.add(reset_button)
    keyboard.add(back_button)

    text = utils.text_to_fat(Keys.CHAPTERS.text)
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


def filter_chapter_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user_chapters = user.filter.chapters

    call_type = CallTypes.parse_data(call.data)
    chapter_id = call_type.chapter_id
    chapter = Chapter.chapters.get(id=chapter_id)

    if chapter.children.exists():
        select_all_button = utils.make_inline_button(
            text=Keys.SELECT_ALL.text,
            CallType=CallTypes.FilterChapterSelectAll,
            chapter_id=chapter.id,
        )
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(select_all_button)
        for child in chapter.children.all():
            chapter_selected = user_chapters.filter(id=child.id).exists()
            smiles = [Smiles.OFF.text, Smiles.ON.text]
            text = f'{child.name} {smiles[chapter_selected]}'
            chapter_button = utils.make_inline_button(
                text=text,
                CallType=CallTypes.FilterChapter,
                chapter_id=child.id,
            )
            keyboard.add(chapter_button)

        reset_button = utils.make_inline_button(
            text=Keys.RESET.text,
            CallType=CallTypes.FilterChapterReset,
            chapter_id=chapter.id,
        )
        back_button = utils.make_inline_button(
            text=Keys.CHAPTERS.text,
            CallType=CallTypes.FilterChapters,
        )
        keyboard.add(reset_button)
        keyboard.add(back_button)
        bot.edit_message_text(
            text=utils.text_to_fat(chapter.name),
            chat_id=chat_id,
            message_id=call.message.id,
            reply_markup=keyboard,
        )
    else:
        if user_chapters.filter(id=chapter.id):
            user_chapters.remove(chapter)
        else:
            user_chapters.add(chapter)

        call_type = CallTypes.FilterChapter(chapter_id=chapter.parent.id)
        call_data = CallTypes.make_data(call_type)
        call.data = call_data
        filter_chapter_call_handler(bot, call)


def filter_chapter_select_all_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user_chapters = user.filter.chapters

    call_type = CallTypes.parse_data(call.data)
    chapter_id = call_type.chapter_id
    chapter = Chapter.chapters.get(id=chapter_id)

    for child in chapter.children.all():
        user_chapters.add(child)

    call_type = CallTypes.FilterChapter(chapter_id=chapter.id)
    call_data = CallTypes.make_data(call_type)
    call.data = call_data
    filter_chapter_call_handler(bot, call)


def filter_chapter_reset_call_handler(bot: telebot.TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.users.get(chat_id=chat_id)
    user_chapters = user.filter.chapters

    call_type = CallTypes.parse_data(call.data)
    chapter_id = call_type.chapter_id
    if not chapter_id:
        user_chapters.clear()
        call_type = CallTypes.FilterChapters()
        call_data = CallTypes.make_data(call_type)
        call.data = call_data
        filter_chapters_call_handler(bot, call)
    else:
        chapter = Chapter.chapters.get(id=chapter_id)
        for child in chapter.children.all():
            user_chapters.remove(child)

        call_type = CallTypes.FilterChapter(chapter_id=chapter.id)
        call_data = CallTypes.make_data(call_type)
        call.data = call_data
        filter_chapter_call_handler(bot, call)
