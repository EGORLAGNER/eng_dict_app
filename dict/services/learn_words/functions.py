from django.contrib.auth.models import User

from dict.models import Word
from random import randint


# def get_all_words():
#     """Набор слов - это выборка, взятая для изучения.
#     Пока что для упрощения, набор слов - это все слова имеющиеся в базе"""
#
#     return Word.objects.all()


def change_rating(rus_value_word, increase_rating=False):
    """Увеличивает или уменьшает рейтинг слов.
    По умолчанию - уменьшает."""

    if increase_rating:
        word = Word.objects.get(rus=rus_value_word)
        current_rating = word.rating
        word.rating = current_rating + 2
        word.save()
    else:
        word = Word.objects.get(rus=rus_value_word)
        current_rating = word.rating
        word.rating = current_rating - 3
        word.save()


def get_all_user_words(username):
    """Набор слов - это выборка, взятая для изучения.
    Пока что для упрощения, набор слов - это все слова имеющиеся в базе"""

    user = User.objects.get(username=username)
    return user.word_set.all()


def get_count_words_in_set(set_words):
    """Возвращает количество слов в наборе"""

    return set_words.count() - 1


def get_random_numbers(set_words):
    """Возвращает список со случайными числами."""

    unique_numbers = []

    last_value = get_count_words_in_set(set_words)
    # Пока список не содержит 4 уникальных числа, продолжаем генерировать случайные числа
    while len(unique_numbers) < 4:
        random_number = randint(0, last_value)
        if random_number not in unique_numbers:
            unique_numbers.append(random_number)

    return unique_numbers


def get_four_words(set_words, numbers):
    """Возвращает список с четырьмя рандомными словами"""
    list_words = []
    for number in numbers:
        list_words.append(set_words[number])
    return list_words


def get_current_word(words):
    """Возвращает случайное выбранное текущее слово для изучения"""
    value = randint(0, 3)
    current_word = words[value]
    return current_word


def get_all_answers(words):
    """Возвращает все ответы"""
    return words[0].rus, words[1].rus, words[2].rus, words[3].rus


def learn_words(user):
    set_words = get_all_user_words(user)
    random_numbers = get_random_numbers(set_words)
    list_words = get_four_words(set_words, random_numbers)
    current_word = get_current_word(list_words)
    question_word = current_word.eng  # сам вопрос
    correct_answer = current_word.rus  # сам вопрос
    all_answers = get_all_answers(list_words)

    return question_word, correct_answer, all_answers


if __name__ == '__main__':
    print()
    change_rating('покупать', )
