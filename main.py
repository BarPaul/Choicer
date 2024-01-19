from os import getenv
from datetime import datetime
from keep_alive import keep_alive
from pytz import timezone
from logging import getLogger, INFO, basicConfig, Formatter
from telebot import TeleBot, types
from card_module import Card, is_right, MASTI, NUMS
from json import load, dump
import time


DATA = load(open('./data.json'))
PRINT_NUMS = [str(i) for i in range(2, 11)] + ["В", "Д", "К", "Т"]
TOKEN = str(getenv("TOKEN"))
MENU = types.ReplyKeyboardMarkup(resize_keyboard=True)
MENU.add("🔝 Начать игру", "🧮 Сбросить счет")
MENU.add("🛟 Помощь", "ℹ️ Информация")
GAME = types.ReplyKeyboardMarkup()
GAME.add("🍏 Легкий", "🍌 Средний", "🌶️ Сложный", "◀️ Вернуться")
bot = TeleBot(TOKEN, parse_mode='markdown')
CARDS = types.ReplyKeyboardMarkup(resize_keyboard=True)
cards, tmp = {
    h2 + a2: h1 + a1
    for h1, h2 in zip(MASTI, ('♦️', '♥️', '♠️', '♣️'))
    for a1, a2 in zip(NUMS, PRINT_NUMS)
}, []
for i, k in enumerate(cards):
  tmp.append(k)
  if len(tmp) % 13 == 0:
    CARDS.row(*tmp)
    tmp = []
CARDS.row(*tmp)
CARDS.add("◀️ Вернуться")
logger = getLogger(__name__)


def timeconverter(*args):
  return datetime.now(timezone('Europe/Moscow')).timetuple()


Formatter.converter = timeconverter
basicConfig(level=INFO,
            format='(%(asctime)s %(levelname)s) Пользователь %(message)s',
            datefmt="%d-%m-%Y %H:%M:%S")
logger.info("запущен!")



def update_data():
  with open('./data.json', 'w') as f:
    dump(DATA, f)


def reset(message: types.Message):
  if message.text.upper() == "ДА":
    logger.warning(
        f"{message.from_user.full_name} ({message.from_user.id}) сбросил свой результат!"
    )
    DATA.pop(str(message.from_user.id))
    update_data()
    return bot.reply_to(message, "Ваши данные были успешно удалены!")
  return bot.reply_to(message, "Удаление отменено!")


@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
  uid = str(message.from_user.id)
  user = DATA.get(uid, None)
  if user is None:
    logger.info(
        f"{message.from_user.full_name} ({message.from_user.id}) зарегистрировался"
    )
    DATA[uid] = {"count": 0, "right": 0, "in_game": False, "points": 0}
    update_data()
  bot.reply_to(
      message,
      f"Привет, *{message.from_user.full_name}*! Поиграем в угадайку?",
      reply_markup=MENU)


@bot.message_handler(content_types=["text"])
def info_command(message: types.Message):
  user = DATA.get(str(message.from_user.id), None)
  if user is None:
    return bot.reply_to(
        message,
        "Ваши данные отсутсвуют в боте! Нажмите /start, чтоб обновить данные")
  if message.text == 'ℹ️ Информация':
    logger.info(
        f"{message.from_user.full_name} ({message.from_user.id}) получает информацию о себе"
    )
    try:
      bot.reply_to(
          message,
          f"Информация о {message.from_user.full_name}\n🔢 Всего ответов: *{user['count']}*\n✅ Правильных ответов: *{user['right']}*\n💯 Твой счет: *{user['points']}*\n⏱️ Точность: *{user['right']/user['count'] * 100:.2f}*%"
      )
    except ZeroDivisionError:
      bot.reply_to(
          message,
          f"Информация о {message.from_user.full_name}\n🔢 Всего ответов: *{user['count']}*\n✅ Правильных ответов: *0*\n💯 Твой счет: *0*\n⏱️ Точность: *0.00*%"
      )
  elif message.text == "🛟 Помощь":
    logger.info(
        f"{message.from_user.full_name} ({message.from_user.id}) получает помощь"
    )
    bot.reply_to(
        message,
        '''> *Как начать игру?* \n> Нажмите на кнопку "_🔝 Начать игру_"\n\n> *Уровни сложности* \n> Есть *3* уровня сложности: легкий, средний, сложный\n> В легком нужно угадать масть, в среднем масть карты, а в сложном \- саму карту\n> За легкий уровень ты получаешь \- 5 очков, средний \- 20 очков и за сложный \- 50 очков\n> *Где посмотреть свои результаты?*\n> Посмотреть свои результаты можно нажав на кнопку "_ℹ️ Информация_", также вы можете поделиться результатами с друзьмями :\)\n\n> *Как сбросить свой результат?*\n> Нажмите на кнопку "_🧮 Сбросить счет_"\n\n> *Нашел ошибку в боте, кому написать?* \n> Напишите [разработчику](https://t.me/PaulBaur) бота в лс\.\n> Всегда рад вашим вопросам, предложениям и сообщениям о багах :\)''',
        parse_mode='markdownV2')
  elif message.text == "🧮 Сбросить счет":
    logger.warning(
        f"{message.from_user.full_name} ({message.from_user.id}) собирается сбросить свой результат!"
    )
    bot.reply_to(
        message,
        "Ты уверен? (напиши да или нет)\n*Это действие нельзя отменить!*")
    bot.register_next_step_handler_by_chat_id(message.chat.id, reset)
  elif message.text == '🔝 Начать игру':
    logger.info(
        f"{message.from_user.full_name} ({message.from_user.id}) перешел к выбору уровней"
    )
    if user['in_game']:
      return bot.reply_to(
          message,
          "Ты уже играешь! Нельзя начать новую игру, не закончив старую")

    bot.reply_to(
        message,
        "Выбери сложность::\n🟢 *Легкий уровень* - угадать цвет масти\n🟡 *Средний уровень* - угадать масть карты\n🔴 *Сложный уровень* - угадать карту\nНажмите кнопку \"◀️ Вернуться\", чтобы перейти в основное меню",
        reply_markup=GAME)
  elif message.text == '◀️ Вернуться':
    logger.info(
        f"{message.from_user.full_name} ({message.from_user.id}) вернулся в главное меню"
    )
    return bot.reply_to(message,
                        "Ты вернулся в главное меню",
                        reply_markup=MENU)
  elif message.text == '🍏 Легкий':
    logger.info(
        f"{message.from_user.full_name} ({message.from_user.id}) выбирает легкий уровень"
    )
    user['in_game'] = True
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🟥 Красный", "⬛ Черный")
    keyboard.add("◀️ Вернуться")
    bot.reply_to(message,
                 "Я загадал карту. Угадай цвет масти :)",
                 reply_markup=keyboard)

    def answer_easy(message: types.Message):

      if message.text == '◀️ Вернуться':
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) возращается в игровое меню"
        )
        user['in_game'] = False
        return bot.reply_to(message,
                            "Ты вернулся в игровое меню",
                            reply_markup=GAME)
      if message.text not in ["🟥 Красный", "⬛ Черный"]:
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) выбирает неверный цвет"
        )
        return bot.reply_to(message, "Неверный цвет!")
      user['in_game'] = False
      user['count'] += 1
      user_card = Card("H" if message.text.startswith("🟥") else "S")
      isrght, ans_card = is_right(user_card)
      logger.info(
          f"{message.from_user.full_name} ({message.from_user.id}) выбирает {message.text}, пока программа выбрала {ans_card}"
      )
      if isrght:
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) получает 5 очков за победу в легком уровне"
        )
        user['points'] += 5
        user['right'] += 1
        bot.send_photo(
            chat_id=message.chat.id,
            reply_to_message_id=message.id,
            caption=
            "✅ Ты угадал!\n +5 очков\nУзнать свой счет можно с помощью кнопки \"Информация\"",
            photo=open(f'./{ans_card[0]}/{ans_card[1:]}.png', 'rb'))
        update_data()
        return bot.register_next_step_handler_by_chat_id(
            message.chat.id, answer_easy)
      bot.send_photo(chat_id=message.chat.id,
                     reply_to_message_id=message.id,
                     caption="❌ Не угадал!",
                     photo=open(f'./{ans_card[0]}/{ans_card[1:]}.png', 'rb'))
      update_data()
      logger.info(
          f"{message.from_user.full_name} ({message.from_user.id}) поражен в легком уровне"
      )
      return bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                       answer_easy)

    return bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                     answer_easy)
  elif message.text == '🍌 Средний':
    logger.info(
        f"{message.from_user.full_name} ({message.from_user.id}) выбирает средний уровень"
    )
    user['in_game'] = True
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("♦️ Бубны", "♥️ Червы", '♠️ Пики', '♣️ Трефы')
    keyboard.add("◀️ Вернуться")
    bot.reply_to(message,
                 "Я загадал карту. Угадай масть :)",
                 reply_markup=keyboard)

    def answer_middle(message: types.Message):
      if message.text == '◀️ Вернуться':
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) возращается в игровое меню"
        )
        user['in_game'] = False
        return bot.reply_to(message,
                            "Ты вернулся в игровое меню",
                            reply_markup=GAME)
      if message.text not in ["♦️ Бубны", "♥️ Червы", '♠️ Пики', '♣️ Трефы']:
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) выбирает неверную масть"
        )
        return bot.reply_to(message, "Неверная масть!")
      user['in_game'] = False
      user['count'] += 1
      masts = {
          "♦️ Бубны": 'D',
          "♥️ Червы": 'H',
          '♠️ Пики': 'S',
          '♣️ Трефы': 'C'
      }
      user_card = Card(masts[message.text], 2)
      isrght, ans_card = is_right(user_card)
      logger.info(
          f"{message.from_user.full_name} ({message.from_user.id}) выбирает {message.text}, а программа выбрала {ans_card}"
      )
      if isrght:
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) получает 20 очков за победу в среднем уровне"
        )
        user['points'] += 20
        user['right'] += 1
        bot.send_photo(
            chat_id=message.chat.id,
            reply_to_message_id=message.id,
            caption=
            "✅ Ты угадал!\n +20 очков\nУзнать свой счет можно с помощью кнопки \"Информация\"",
            photo=open(f'./{ans_card[0]}/{ans_card[1:]}.png', 'rb'))
        update_data()
        return bot.register_next_step_handler_by_chat_id(
            message.chat.id, answer_middle)
      logger.info(
          f"{message.from_user.full_name} ({message.from_user.id}) поражен в среднем уровне"
      )
      bot.send_photo(chat_id=message.chat.id,
                     reply_to_message_id=message.id,
                     caption="❌ Не угадал!",
                     photo=open(f'./{ans_card[0]}/{ans_card[1:]}.png', 'rb'))
      update_data()
      return bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                       answer_middle)

    return bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                     answer_middle)
  elif message.text == '🌶️ Сложный':
    logger.info(
        f"{message.from_user.full_name} ({message.from_user.id}) выбирает сложный уровень"
    )
    user['in_game'] = True
    bot.reply_to(message,
                 "Я загадал карту. Угадай карту :)",
                 reply_markup=CARDS)

    def answer_hard(message: types.Message):
      if message.text == '◀️ Вернуться':
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) возращается в игровое меню"
        )
        user['in_game'] = False
        return bot.reply_to(message,
                            "Ты вернулся в игровое меню",
                            reply_markup=GAME)
      if message.text not in cards.keys():
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) выбирает неверную карту"
        )
        return bot.reply_to(message, "Неверная карта!")
      user['in_game'] = False
      user['count'] += 1
      user_card = Card(cards[message.text], 3)
      isrght, ans_card = is_right(user_card)
      logger.info(
          f"{message.from_user.full_name} ({message.from_user.id}) выбирает {message.text}, пока программа выбрала {ans_card}"
      )
      if isrght:
        logger.info(
            f"{message.from_user.full_name} ({message.from_user.id}) выигрывает 50 очков за победу в сложном уровне"
        )
        user['points'] += 50
        user['right'] += 1
        bot.send_photo(
            chat_id=message.chat.id,
            reply_to_message_id=message.id,
            caption=
            "✅ Ты угадал!\n +50 очков\nУзнать свой счет можно с помощью кнопки \"Информация\"",
            photo=open(f'./{ans_card[0]}/{ans_card[1:]}.png', 'rb'))
        update_data()
        return bot.register_next_step_handler_by_chat_id(
            message.chat.id, answer_hard)
      logger.info(
          f"{message.from_user.full_name} ({message.from_user.id}) поражен в сложном уровне"
      )
      bot.send_photo(chat_id=message.chat.id,
                     reply_to_message_id=message.id,
                     caption="❌ Не угадал!",
                     photo=open(f'./{ans_card[0]}/{ans_card[1:]}.png', 'rb'))
      update_data()
      return bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                       answer_hard)

    return bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                     answer_hard)


if __name__ == '__main__':
  keep_alive()
  bot.infinity_polling(none_stop=True)
