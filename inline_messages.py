from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

EMPTY_MESSAGE = InlineQueryResultArticle(
    id='empty',
    title=f'Send premium exclusive message',
    input_message_content=InputTextMessageContent("Enter message"),
    description='Write message to users of the same premium',
    thumb_url='https://i.imgur.com/FkPJjhk.jpg'
)

TOO_LONG = InlineQueryResultArticle(
    id='empty',
    title=f'Your message is too long',
    input_message_content=InputTextMessageContent("Message should not be longer than 200 symbols"),
    description='Message should not be longer than 200 symbols',
    thumb_url='https://i.imgur.com/9G9BpSH.jpg'
)

READ_MARKUP = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Read this message', callback_data='wait'))

PREMIUM_MESSAGE = InlineQueryResultArticle(
    id='prem',
    title=f'Send message for premium users',
    input_message_content=InputTextMessageContent(
        f'This message is only available for *Telegram Premium*™ users',
        parse_mode='Markdown'
    ),
    reply_markup=READ_MARKUP,
    description='You are a premium user, this message will be available only to premium users',
    thumb_url='https://i.imgur.com/FkPJjhk.jpg',
)

BROKE_MESSAGE = InlineQueryResultArticle(
    id='non-prem',
    title=f'Send message for broke users',
    input_message_content=InputTextMessageContent(
        f'This message is only available for *Broke Telegram* users',
        parse_mode='Markdown'
    ),
    reply_markup=READ_MARKUP,
    description='You are a non-premium user, this message will be available only to broke users',
    thumb_url='https://i.imgur.com/FkPJjhk.jpg',
)

LIMITED_MARKUP = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Read this message', callback_data='waitLimit'))
WAIT_MARKUP = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Wait', callback_data='wait'))

LIMITED_READ_MESSAGE = InlineQueryResultArticle(
    id='wait',
    title=f'Send message with limited life',
    input_message_content=InputTextMessageContent(
        f'This message is *exclusive*. It could be seen only limited amount of times!',
        parse_mode='Markdown'
    ),
    reply_markup=LIMITED_MARKUP,
    description='To set limit number write message like `number message` (default is 1)',
    thumb_url='https://i.imgur.com/5xndy07.jpg',
)

BEER_MESSAGE = InlineQueryResultArticle(
    id='beer',
    title=f'Get random beer photo',
    input_message_content=InputTextMessageContent(
        'Pouring beer...',
        parse_mode='Markdown',
        disable_web_page_preview=False
    ),
    reply_markup=WAIT_MARKUP,
    description='Get random beer photo!',
    thumb_url='https://i.imgur.com/Cx3Is9r.jpg',
)
