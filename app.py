import asyncio
from os import getenv
import logging
from json import loads


from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, ChosenInlineResult
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import CallbackQuery, Message

import firebase_admin
from firebase_admin import db

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
    text = inline_query.query.strip()
    raw_json: dict = loads(inline_query.from_user.as_json())
    temp_memory[inline_query.from_user.id] = ''

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Read this message', callback_data='wait'))

    if len(text) == 0:
        write_message = InlineQueryResultArticle(
            id='empty',
            title=f'Send message for premium users',
            input_message_content=InputTextMessageContent("Enter message"),
            description='Write some text that you want to send to premium users',
            thumb_url='https://i.imgur.com/FkPJjhk.jpg'
        )
        await inline_query.answer([write_message], cache_time=0)
    elif len(text) > 200:
        too_long = InlineQueryResultArticle(
            id='empty',
            title=f'Your message is too long',
            input_message_content=InputTextMessageContent("Message should not be longer than 200 symbols"),
            description='Message should not be longer than 200 symbols',
            thumb_url='https://i.imgur.com/9G9BpSH.jpg'
        )
        await inline_query.answer([too_long], cache_time=0)
    elif is_premium(raw_json):
        premium_item = InlineQueryResultArticle(
            id='prem',
            title=f'Send message for premium users',
            input_message_content=InputTextMessageContent(
                f'This message is only available for *Telegram Premium*™ users',
                parse_mode='Markdown'
            ),
            reply_markup=markup,
            description='You are a premium user, this message will be available only to premium users',
            thumb_url='https://i.imgur.com/FkPJjhk.jpg',
        )
        temp_memory[inline_query.from_user.id] = text
        await inline_query.answer([premium_item], cache_time=0)
    else:
        non_premium_item = InlineQueryResultArticle(
            id='non-prem',
            title=f'Send message for premium users:',
            input_message_content=InputTextMessageContent(
                'I am *NOT a premium* user, so here is my message:\n\n' + text,
                parse_mode='Markdown'
            ),
            reply_markup=markup,
            description='You are not a premium user, your message will be available for everyone',
            thumb_url='https://i.imgur.com/FkPJjhk.jpg',
        )
        await inline_query.answer([non_premium_item], cache_time=0)


@dp.chosen_inline_handler()
async def chosen_result(chosen_inline: ChosenInlineResult):
    result_id = chosen_inline.result_id
    inline_id = chosen_inline.inline_message_id
    if result_id != 'prem' or inline_id is None:
        return
    user_id = chosen_inline.from_user.id

    ref = db.reference('/messages')
    key = ref.push(temp_memory[user_id]).key

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Read this message', callback_data=key))
    await bot.edit_message_reply_markup(inline_message_id=inline_id, reply_markup=markup)


@dp.callback_query_handler()
async def question_menu_callback(callback_query: CallbackQuery):
    raw_json: dict = loads(callback_query.from_user.as_json())
    callback_data = callback_query.data

    if not is_premium(raw_json):
        await callback_query.answer('You must subscribe to Telegram Premium™ to read this message', show_alert=True)
    elif callback_data == 'wait':
        await callback_query.answer('Please wait a second to see the result', show_alert=False)
    else:
        ref = db.reference('/messages/' + callback_data)
        await callback_query.answer(str(ref.get()), show_alert=True)


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
