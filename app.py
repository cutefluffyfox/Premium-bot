from os import getenv, environ
import hashlib
import logging
from json import loads

from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineQueryResultPhoto
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())
BOT_TOKEN = getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def is_premium(json: dict) -> bool:
    return json.get('is_premium', False)


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    text = inline_query.query.strip()
    raw_json: dict = loads(inline_query.from_user.as_json())

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Read this message', callback_data=text))
    result_id: str = hashlib.md5(text.encode()).hexdigest()

    premium_item = InlineQueryResultArticle(
        id=result_id,
        title=f'Send message for premium users',
        input_message_content=InputTextMessageContent(
            f'This message is only available for *Telegram Premium*™ users',
            parse_mode='Markdown'
        ),
        description='You are a premium user, this message will be available only to premium users',
        reply_markup=markup,  # Limit 32 characters, todo make it to 200
        thumb_url='https://i.imgur.com/FkPJjhk.jpg',
    )
    non_premium_item = InlineQueryResultArticle(
        id=result_id,
        title=f'Send message for premium users:',
        input_message_content=InputTextMessageContent(
            'I am *NOT a premium* user, so here is my message:\n\n' + text,
            parse_mode='Markdown'
        ),
        description='You are not a premium user, your message will be available for everyone',
        thumb_url='https://i.imgur.com/FkPJjhk.jpg',
    )
    if text:
        await inline_query.answer([premium_item if is_premium(raw_json) else non_premium_item])


@dp.callback_query_handler()
async def question_menu_callback(callback_query: CallbackQuery):
    raw_json: dict = loads(callback_query.from_user.as_json())
    if is_premium(raw_json):
        await callback_query.answer(callback_query.data, show_alert=True)
    else:
        await callback_query.answer('You must subscribe to Telegram Premium™ to read this message', show_alert=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
