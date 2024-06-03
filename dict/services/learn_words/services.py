from django.core import serializers
from dict.models import *

import random


def _get_words_by_selected_categories(categories):
    """
    Вернет все слова согласно выбранным категориям
    """
    return Word.objects.filter(category__slug__in=categories).distinct()[:3]


def _get_words_data(queryset):
    """
    Возвращает список со словарями.
    Словари хранят в себе данные слов, необходимые для процесса изучения слов.
    """

    data = []

    for word in queryset:
        word_id = word.id
        eng = word.eng
        rus = word.rus

        word_data = {'word_id': word_id,
                     'eng': eng,
                     'rus': rus,
                     'correct_answer': None,
                     'incorrect_answer': None}

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
    words_data = _get_words_data(words)

    # перемешать список
    random.shuffle(words_data)

    # словарь со всеми данными, для сохранения в сессии
    dataset = {
        'words_data': words_data,
        'unsaved_words_statistics': unsaved_words_statistics,
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
        set_flag_true(request, 'is_are_words_exhausted')
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
    for item in list(objects):
        model_objects.append(item.object)

    return model_objects


def convert_deserialize_objects_to_json(objects):
    return serializers.serialize('json', objects)


# ==========================================================

def get_current_word(request):
    return request.session.get('current_word', False)


def get_user_answer(request):
    return request.POST.get('user_answer', False)


def get_correct_answer(request):
    """Пучить правильный ответ."""
    current_word_data = get_current_word(request)
    return current_word_data.get('rus', False)


def is_user_give_correct_answer(request):
    """Оценка правильности ответа пользователя."""
    user_answer = get_user_answer(request)
    correct_answer = get_correct_answer(request)

    if user_answer == correct_answer:
        return True
    return False


def _append_current_word_data_in_unsaved_words_statistics(request, current_word_data):
    unsaved_words_statistics = request.session['dataset'].get('unsaved_words_statistics')
    return unsaved_words_statistics.append(current_word_data)


def save_updated_words_statistics_in_session(request, user_give_correct_answer=False):
    current_word_data = get_current_word(request)
    if not user_give_correct_answer:
        current_word_data['correct_answer'] = False
        return _append_current_word_data_in_unsaved_words_statistics(request, current_word_data)

    current_word_data['correct_answer'] = True
    return _append_current_word_data_in_unsaved_words_statistics(request, current_word_data)


def _get_unsaved_words_statistics_from_session(request):
    return request.session['dataset'].get('unsaved_words_statistics')


def _get_json_words_from_session(request):
    return request.session['dataset'].get('json_words')


def _deserialize_json(json):
    return serializers.deserialize('json', json)


def updates_words_statistics_in_db(request):
    words_statistics = _get_unsaved_words_statistics_from_session(request)
    json = _get_json_words_from_session(request)
    deserialize_objects = _deserialize_json(json)
    words_objects = get_model_objects_from_deserialized_objects(deserialize_objects)
    print()
    print()


def print_super_list(request, message, value_for_append=False):
    if not value_for_append:
        print(request.session['super_list'])
        print()
        return
    print(message)
    request.session['super_list'].append(value_for_append)
    print(request.session['super_list'])
    print()
