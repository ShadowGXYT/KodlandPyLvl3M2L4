import telebot
from config import token
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logic import TextAnalysis

bot = telebot.TeleBot(token)

LANGS = {
    "de": "Deutsch",
    "en": "English",
    "ru": "Русский",
}

translation_state = {}


def typing_effect(chat_id):
    try:
        bot.send_chat_action(chat_id, action='typing')
    except Exception:
        pass


def ask_language(chat_id, field, text):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(label, callback_data=f"set_lang:{field}:{code}")
        for code, label in LANGS.items()
    ]
    markup.add(*buttons)
    bot.send_message(chat_id, text, reply_markup=markup)


def gen_markup_for_text():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton('Получить ответ', callback_data='text_ans'),
        InlineKeyboardButton('Перевести сообщение', callback_data='text_translate')
    )
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_lang:'))
def set_language(call):
    _, field, lang_code = call.data.split(':')
    username = call.from_user.username or str(call.from_user.id)
    state = translation_state.setdefault(username, {})
    state[field] = lang_code

    if field == 'from_lang':
        ask_language(call.message.chat.id, 'to_lang', 'Теперь выбери язык перевода:')
    elif field == 'to_lang':
        from_lang = state.get('from_lang')
        to_lang = state.get('to_lang')

        if from_lang and to_lang:
            bot.send_message(
                call.message.chat.id,
                f"Отлично! Теперь отправь текст для перевода с {LANGS[from_lang]} на {LANGS[to_lang]}"
            )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if not call.data or 'text' not in call.data:
        return

    username = call.from_user.username or str(call.from_user.id)
    if username not in TextAnalysis.memory or not TextAnalysis.memory[username]:
        return

    obj = TextAnalysis.memory[username][-1]
    response_text = getattr(obj, 'response', obj.translation)
    translation_text = getattr(obj, 'translation', response_text)

    if call.data == "text_ans":
        typing_effect(call.message.chat.id)
        bot.send_message(call.message.chat.id, response_text)
    elif call.data == "text_translate":
        typing_effect(call.message.chat.id)
        bot.send_message(call.message.chat.id, translation_text)


@bot.message_handler(commands=['translate'])
def start_translate(message):
    username = message.from_user.username or str(message.from_user.id)
    translation_state[username] = {}
    ask_language(message.chat.id, 'from_lang', 'Выбери исходный язык:')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    username = message.from_user.username or str(message.from_user.id)
    state = translation_state.get(username)

    if message.text == '/translate':
        start_translate(message)
        return

    if state is not None and state.get('from_lang') and state.get('to_lang'):
        from_lang = state['from_lang']
        to_lang = state['to_lang']
        obj = TextAnalysis(message.text, username, from_lang, to_lang)
        typing_effect(message.chat.id)
        bot.send_message(message.chat.id, f"Перевод: {obj.translation}")
        translation_state.pop(username, None)
        return

    TextAnalysis(message.text, username)
    typing_effect(message.chat.id)
    bot.send_message(
        message.chat.id,
        "Я получил твое сообщение! Что ты хочешь с ним сделать?",
        reply_markup=gen_markup_for_text()
    )


bot.infinity_polling(none_stop=True)
