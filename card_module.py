from contextlib import suppress
from random import choice


if __name__ == '__main__':
  MASTI, NUMS = ('Б', 'Ч', 'П', 'Т'), [str(i) for i in range(2, 11)] + ["К", "В", "Д", "Т"]
else:
  MASTI, NUMS = ('D', 'H', 'S', 'C'), [str(i) for i in range(2, 11)] + ["K", "J", "Q", "A"]

class Card:
  def __init__(self, card: str, mode=1):
    self.card = card
    self.mode = mode

  @classmethod
  def generate_card(cls):
    cls.card = choice(MASTI) + choice(NUMS)
    return cls  
  
  def __eq__(self, other):
    if self.mode == 3:
      return self.card == other.card
    elif self.mode == 2:
      return self.card[0] == other.card[0]
    return (self.card[0] in ('Б', 'Ч')) == (other.card[0] in ('Б', 'Ч')) if __name__ == '__main__' else (self.card[0] in ('H', 'D')) == (other.card[0] in ('H', 'D'))

def is_right(user_card: Card):
  global answered
  answer_card = Card.generate_card()
  if user_card == answer_card:
    if __name__ == '__main__':
      answered += 1  
    return f"Ты угадал! Карта: {answer_card.card}" if __name__ == '__main__' else (True, answer_card.card)
  return f"Не угадал. Карта: {answer_card.card}" if __name__ == '__main__' else (False, answer_card.card)
  

def game():
  global answered, cnt
  print("1 - легкая сложность\n2 - средняя сложность\n3 - сложная сложность")
  match input("Выберите сложность: "):
    case '1':
      print("Угадай цвет масти (Черная или Красная)")
      mast = input("Введи цвет (только первая буква): ").upper()
      if mast not in ["Ч", "К"]:
        return print("Неверный цвет масти!\nДоступные цвета: Ч, К")
      print(is_right(Card("Б" if mast == "К" else "П")))
    case '2':
      print("Угадай масть (" + ', '.join(MASTI) + ')')
      mast = input("Введи масть (только первая буква): ").upper()
      if mast not in MASTI:
        return print("Неверная масть!\nДоступные масти: " + ', '.join(MASTI))
      print(is_right(Card(mast, 2)))
    case '3':
      print("Угадай карту")
      mast = input("Введи карту (Одну букву масти + достоинство карты): ").upper()
      if mast[0] not in MASTI:
        return print("Неверная масть!\nДоступные масти: " + ', '.join(MASTI))
      elif mast[1:] not in NUMS:
        return print("Неверное достоинство!\nДоступные достоинства: " + ', '.join(NUMS))
      print(is_right(Card(mast, 3)))
    case '':
      print("Пока, пока!")
      exit()
    case _:
      print("Неверная сложность!")
      cnt -= 1
  cnt += 1
  with suppress(ZeroDivisionError):
    print(f"Раунд {cnt} окончен. Правильные ответы {round(answered / cnt * 100, 1)}%")

if __name__ == '__main__':
  cnt, answered = 0, 0
  while True:
    game()
