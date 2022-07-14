import asyncio
from os import getenv
import logging
from json import loads
from collections import OrderedDict

from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, ChosenInlineResult
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton
from aiogram.types import CallbackQuery, Message

import firebase_admin
from firebase_admin import db
import inline_messages

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
BOT_TOKEN = getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

firebase_admin.initialize_app(
    firebase_admin.credentials.Certificate('firebase.json'),
    {'databaseURL': getenv('FIREBASE_URL')}
)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
temp_memory = dict()


def is_premium(json: dict) -> bool:
    return json.get('is_premium', False)


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    user_id = inline_query.from_user.id
    text = inline_query.query.strip()
    raw_json: dict = loads(inline_query.from_user.as_json())
    temp_memory[inline_query.from_user.id] = ''

    if len(text) == 0:
        await inline_query.answer([inline_messages.EMPTY_MESSAGE], cache_time=0)
    elif len(text) >= 200:
        await inline_query.answer([inline_messages.TOO_LONG], cache_time=0)
    elif is_premium(raw_json):
        temp_memory[user_id] = text
        await inline_query.answer([inline_messages.PREMIUM_MESSAGE], cache_time=0)
    else:
        temp_memory[user_id] = text
        await inline_query.answer([inline_messages.BROKE_MESSAGE], cache_time=0)


@dp.chosen_inline_handler()
async def chosen_result(chosen_inline: ChosenInlineResult):
    result_id = chosen_inline.result_id
    inline_id = chosen_inline.inline_message_id
    if result_id not in ['prem', 'non-prem'] or inline_id is None:
        return
    user_id = chosen_inline.from_user.id
    raw_json: dict = loads(chosen_inline.from_user.as_json())

    ref = db.reference('/messages')
    key = ref.push({'text': temp_memory[user_id], 'premium': is_premium(raw_json)}).key

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Read this message', callback_data=key))
    await bot.edit_message_reply_markup(inline_message_id=inline_id, reply_markup=markup)


@dp.callback_query_handler()
async def question_menu_callback(callback_query: CallbackQuery):
    raw_json: dict = loads(callback_query.from_user.as_json())
    callback_data = callback_query.data
    message: OrderedDict = db.reference('/messages/' + callback_data).get()

    if callback_data == 'wait':
        await callback_query.answer('Please wait a second to see the result', show_alert=False)
    elif is_premium(raw_json) == message.get('premium', True):
        await callback_query.answer(str(message.get('text')), show_alert=True)
    elif is_premium(raw_json):
        await callback_query.answer('You are too rich to read this message', show_alert=True)
    else:
        await callback_query.answer('You must subscribe to Telegram Premium™ to read this message', show_alert=True)


@dp.message_handler(commands=['remove_keyboard'])
async def remove_keyboard(message: Message):
    sample_markup = ReplyKeyboardMarkup(one_time_keyboard=False)
    sample_markup.add(KeyboardButton('/remove_keyboard'))
    message1 = await message.answer(
        text='Set new keyboard',
        reply_markup=sample_markup
    )
    await asyncio.sleep(0.5)
    message2 = await message.answer(
        text='Deleted keyboard',
        reply_markup=ReplyKeyboardRemove()
    )
    await bot.delete_message(chat_id=message1.chat.id, message_id=message1.message_id)
    await bot.delete_message(chat_id=message2.chat.id, message_id=message2.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
