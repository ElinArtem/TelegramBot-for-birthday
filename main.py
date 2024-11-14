import telebot
import requests
from telebot import types
from config import settings
from help_function import conect_json, save_to_json

bot = telebot.TeleBot(settings["TOKEN"])

poll_results = {}


@bot.message_handler(commands=["start"])
def start(message: types.Message):

    users = conect_json("all_users.json")
    user_info = {
        "id": message.from_user.id,
        "name": message.from_user.full_name,
        "username": (
            f"@{message.from_user.username}" if message.from_user.username else "N/A"
        ),
    }
    if user_info not in users:
        users.append(user_info)
        save_to_json(users, "all_users.json")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("ℹ️ подробности ℹ️")
    markup.add(item1)

    mess = (
        f"Привет, {message.from_user.first_name}!\n\n"
        "Я предвкушаю с нетерпением нашу встречу, чтобы разделить впечатления о Дубае и отпраздновать мой День Рождения!\n\n"
        "Это путешествие не будет привычным или стандартным.\nМы с Олесей приготовили нечто особенное!\n\n"
        "Чтобы узнать больше о нашем путешествии, нажмите на кнопку <b>ℹ️ подробности ℹ️</b>"
    )

    bot.send_message(message.chat.id, mess, parse_mode="html", reply_markup=markup)


@bot.message_handler(commands=["ℹ️ подробности ℹ️"])
def dop_info(message: types.Message) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("жду встречи")
    item2 = types.KeyboardButton("очень жду встречи")
    markup.row(item1, item2)

    bot.send_video(message.chat.id, settings["video_details"], reply_markup=markup)


def create_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("✉️ приглашение ✉️")
    item2 = types.KeyboardButton("🎒 что взять с собой 🎒")
    item3 = types.KeyboardButton("👗 дресс-код 👗")
    item4 = types.KeyboardButton("👩 организаторы 👩")
    markup.add(item1, item2, item3, item4)
    return markup


@bot.message_handler(content_types=["text"])
def main(message: types.Message):
    text = message.text.lower()
    markup = create_main_markup()

    if text == "ℹ️ подробности ℹ️":
        dop_info(message)
    elif text == "✉️ приглашение ✉️":
        bot.send_document(message.chat.id, settings["invitation"], reply_markup=markup)
    elif text == "🎒 что взять с собой 🎒":
        mess = (
            "1. Документы:\n- Паспорт\n- Свидетельство о рождении для детей\n\n"
            "2. Одежда:\n- Легкая, дышащая одежда для жары.\n- Купальник для пляжа и бассейна.\n- Удобная обувь для прогулок.\n\n"
            "3. Солнцезащитные средства:\n- Солнцезащитный крем с высоким SPF.\n- Солнцезащитные очки.\n- Головной убор\n\n"
            "4. Личные вещи:\n- Аптечка с основными лекарствами"
        )
        bot.send_message(message.chat.id, mess, reply_markup=markup)
    elif text == "👗 дресс-код 👗":
        mess = (
            "На праздничный ужин 20 августа просим быть в total black или total white. И приветствуются аксессуары серебряного цвета.\n"
            "*Рекомендуем выбрать натуральные дышащие ткани. Дубай любит радовать жаркой погодой."
        )
        image = settings["image_dress_code"]
        bot.send_photo(
            message.chat.id, image, mess, parse_mode="html", reply_markup=markup
        )
    elif text == "👩 организаторы 👩":
        mess = (
            "Если захочешь сделать сюрприз для именинника или у тебя возникнут любые другие вопросы, пиши организаторам.\n\n"
            "Зара +971 58 506 5089\nВиктория +971 56 570 9186"
        )
        bot.send_message(message.chat.id, mess, reply_markup=markup)
    elif text in ["жду встречи", "очень жду встречи"]:
        bot.send_message(
            message.chat.id,
            "Это прекрасно! И мы тебя с нетерпением ждем!",
            reply_markup=markup,
        )
    elif text == "poll":
        send_poll(message)
    else:
        mess = (
            "Дорогой друг!\n"
            "Я - информационный бот, в котором ты можешь узнать о предстоящем мероприятии!\n"
            "Если у тебя возникли вопросы, ты можешь обратиться к организаторам. Чтобы узнать их контакты, напиши мне <b>👩 организаторы 👩</b> или нажми на соответствующую кнопкк."
        )
        bot.send_message(message.chat.id, mess, parse_mode="html", reply_markup=markup)


def send_poll(id: int):
    question = (
        "Дорогой друг 🤍"
        "Выбери алкоголь, который ты предпочитаешь."
        "Можно несколько вариантов)"
    )
    options = [
        "Шампанское/Проссеко 🥂",
        "Виски 🥃",
        "Белое вино",
        "Красное вино 🍷",
        "Пиво 🍻",
        "Егермейстер",
    ]
    # Отправка опроса и сохранение ID опроса
    poll_message = bot.send_poll(
        chat_id=id,
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    # Инициализация пустого списка для сохранения ответов
    poll_results[poll_message.poll.id] = {}


@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    user_id = poll_answer.user.id
    name = poll_answer.user.full_name
    poll_id = poll_answer.poll_id
    option_ids = poll_answer.option_ids

    alco = conect_json("alco.json")

    # Сохраняем ответы пользователя
    poll_results[poll_id][user_id] = option_ids

    # Дополнительно можно вывести результат в консоль или записать в файл
    alco.append(
        {
            "user_id": user_id,
            "name": name,
            "poll_id": poll_id,
            "option_ids": option_ids,
        }
    )

    save_to_json(alco, "alco.json")

    print(
        f"Пользователь {user_id}, {name} выбрал вариант(ы) {option_ids} в опросе {poll_id}."
    )


bot.polling(none_stop=True)



