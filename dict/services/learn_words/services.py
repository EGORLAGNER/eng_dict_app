from django.core import serializers
from dict.models import *

import random


def _get_words_by_selected_categories(categories):
    """
    Вернет все слова согласно выбранным категориям
    """
    return Word.objects.filter(category__slug__in=categories).distinct()


def _get_word_data(queryset):
    """
    Возвращает список со словарями.
    Словари хранят в себе данные слов, необходимые для процесса изучения слов.
    """

    data = []

    for word in queryset:
        word_id = word.id
        eng = word.eng
        rus = word.rus

        word_data = {'word_id': word_id, 'eng': eng, 'rus': rus}

        data.append(word_data)
    return data


def create_dataset(request, categories):
    """
    Генерирует данные (dataset) для процесса изучения слов.
    Сохранят данные в сессии:
    - данные "dataset";
    - флаг "data_ready", указывает на готовность;

    Функция ничего не возвращает.
    """

    # данные изученных слов с измененной статистикой
    unsaved_words_statistics = []

    # достать из базы слова согласно выбранным категориям
    words = _get_words_by_selected_categories(categories)

    # преобразовать объекты моделей Word в JSON
    json_words = serializers.serialize('json', words)

    # получить данные необходимые для изучения слов (самый главный список с полями)
    words_data = _get_word_data(words)

    # перемешать список
    random.shuffle(words_data)

    # словарь со всеми данными, для сохранения в сессии
    dataset = {
        'words_data': words_data,
        'unsaved_word_statistics': unsaved_words_statistics,
        'json_words': json_words
    }

    # сохранение словаря с данными в сессию
    request.session['dataset'] = dataset

    # данные для изучения слов подготовлены
    set_flag_true(request, 'is_dataset_created')

    # # print(f'result Words -> JSON: {json_words}')
    # pprint(json_words)
    #
    # # десериализованные объекты Word в списке
    # deserialize_objects_word = list(serializers.deserialize('json', json_words))
    # print(f'result JSON -> Words: {deserialize_objects_word}')
    #
    # # перемешивание списка десериализованных слов
    # random.shuffle(deserialize_objects_word)
    # print(f'result shuffle list: {deserialize_objects_word}')
    #
    # model_objects_list = get_model_objects_from_deserialized_objects(deserialize_objects_word)
    # print(f'result model objects_list: {model_objects_list}')

    # word = model_objects_list[0]
    # print(f'word: {word}')
    # word.eng = '101'
    # word.statistics.learning_counter = 777
    # word.save()
    # word.statistics.save()


def _get_words_data_from_session(request):
    words_data = request.session['dataset'].get('words_data', False)
    return words_data


def is_are_words_exhausted(request):
    """
    Проверяет, закончились ли слова в списке.
    Если слова закончились - вернет True,
    В противном случае False.
    """
    words_data = _get_words_data_from_session(request)
    if not words_data:
        set_flag_false(request, 'is_dataset_created')
        print('в списке закончились слова')
        return True

    return False


def get_current_words_data(request):
    """
    Функция нарушает принцип единственной ответственности, но так её читать легче.
    """
    # взять список со словами из сессии
    words_data = _get_words_data_from_session(request)

    current_word = words_data.pop()

    # сохранить в сессию, чтобы потом обновить статистику
    # и добавить в список уже изученных/модифицированных слов
    request.session['current_word'] = current_word

    meaning = current_word['eng']
    translation = current_word['rus']

    return meaning, translation


# def get_word_data_list(request):
#     return request.session['dataset'].get('word_data_list', False)
#
#
# def check_and_set_flag(request, word_data_list):
#     if not word_data_list or len(word_data_list) == 0:
#         set_flag_false(request, 'data_ready')
#         return False
#     return True
#
#
# def save_current_word_to_session(request, current_word):
#     request.session['current_word'] = current_word
#
#
# def get_meaning_and_translation(request):
#     word_data_list = get_word_data_list(request)
#     if not check_and_set_flag(request, word_data_list):
#         return
#
#     current_word = word_data_list.pop()
#     save_current_word_to_session(request, current_word)
#     meaning = current_word['eng']
#     translation = current_word['rus']
#     return meaning, translation


def get_random_incorrect_answers(request, value_answers):
    incorrect_answers = get_or_create_incorrect_answers(request)
    answers = random.choices(k=value_answers, population=incorrect_answers)
    return answers


def get_question_and_answers(request):
    question, correct_answer = get_current_words_data(request)

    answers = get_random_incorrect_answers(request, 3)

    answers.append(correct_answer)

    random.shuffle(answers)
    return question, correct_answer, answers


def is_created_dataset(request):
    return get_flag(request, 'is_dataset_created')


def get_selected_categories(request):
    return request.session.get('selected_categories', False)


def _save_incorrect_answers_in_session(request, answers):
    request.session['incorrect_answers'] = answers


def _generate_incorrect_answers():
    """
    Вернет список вариантов не правильных ответов
    """
    queryset = Word.objects.all().distinct()[0:100].values_list('rus', flat=True)
    incorrect_answers = [answer for answer in queryset]
    random.shuffle(incorrect_answers)
    return incorrect_answers


def get_or_create_incorrect_answers(request):
    incorrect_answers = request.session.get('incorrect_answers', False)

    if not incorrect_answers:
        incorrect_answers = _generate_incorrect_answers()
        _save_incorrect_answers_in_session(request, incorrect_answers)

    return incorrect_answers


def set_flag_true(request, variable_name):
    flag_name = variable_name + '_flag'
    request.session[flag_name] = True


def set_flag_false(request, variable_name):
    flag_name = variable_name + '_flag'
    request.session[flag_name] = False


def get_flag(request, variable_name):
    variable_name = variable_name + '_flag'
    value = request.session.get(variable_name, False)
    if not isinstance(value, bool):
        raise TypeError(f'request.session.{variable_name} является {type(value)}, а должен {bool}')
    if value:
        return True
    return False


def get_model_objects_from_deserialized_objects(objects):
    model_objects = []
    for item in objects:
        model_objects.append(item.object)

    return model_objects


def convert_deserialize_objects_to_json(objects):
    return serializers.serialize('json', objects)
