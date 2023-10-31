import pandas as pd
from dict.models import Word, Part
from django.db.utils import IntegrityError
from config.settings import PATH_EXCEL_FILE

EXCEL_DATA_FILE = PATH_EXCEL_FILE


def _check_value_is_string(*args):
    """Возвращает True, если переданное значение является строкой"""
    for value in args:
        if isinstance(value, str):
            return True
        else:
            return False


def _check_value_is_bool(*args):
    """Возвращает True, если переданное значение является логическим"""
    for value in args:
        if isinstance(value, bool):
            return True
        else:
            return False


def _get_data_from_excel(columns_range, rows_range, sheet_name):
    """Возвращает список со словарями, которые содержат данные:
        ключ - название ячейки;
        значение - значение ячейки;

    Аргументы:
        columns_range - str, диапазон колонок для чтения, например 'A:F'
        rows_range - int, номер строки, до которой читать файл, например 1000.
        sheet_name - str, название страницы в excel файле, например 'words'

    Excel файл должен лежать рядом с данным python файлом."""

    file_path = EXCEL_DATA_FILE

    # Прочитать данные с указанной страницы в DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=columns_range, nrows=rows_range)

    # Преобразовать DataFrame в словарь
    list_with_dicts = df.to_dict(orient='records')

    # data_dict теперь содержит данные в формате словаря
    return list_with_dicts


def _add_words_in_db(list_with_dict):
    """Добавляет в базу данных части речи (Word)"""
    count_add_words = 0
    for dictionary in list_with_dict:
        eng = dictionary['eng']
        rus = dictionary['rus']
        is_popular = dictionary['popular']
        is_it = dictionary['it']
        print(dictionary)

        if type(rus) is not str:
            rus = None

        if is_popular is not True:
            is_popular = False

        if is_it is not True:
            is_it = False

        try:
            if (_check_value_is_string(eng) and
                    _check_value_is_bool(is_popular) and _check_value_is_bool(is_it)):

                Word.objects.create(
                    eng=eng.lower(),
                    rus=rus,
                    is_popular=is_popular,
                    is_it=is_it,
                    user_id=1
                )
                print('добавлено')
                count_add_words = count_add_words + 1
            else:
                print('пропущено')
                continue
        except IntegrityError:
            continue

    print(f'Добавлено слов в базу: {count_add_words}')
    print(f'Всего слов в базе: {Word.objects.all().count()}')


def _add_parts_in_db(list_with_dict):
    """Добавляет в базу данных части речи (Part)"""
    for dictionary in list_with_dict:
        eng = dictionary['eng']
        rus = dictionary['rus']
        description = dictionary['description']

        Part.objects.create(
            eng=eng.lower(),
            rus=rus.lower(),
            description=description.lower(),
        )


def start_process_add_parts_in_db(flag=False):
    """Запускает процесс добавления частей речи (Part) в базу данных"""

    data_set_with_parts = _get_data_from_excel(
        'A:C',
        10,
        'parts',
    )

    if flag:
        _add_parts_in_db(data_set_with_parts)
        print('Импорт ЧАСТЕЙ РЕЧИ в базу завершен!')
    return data_set_with_parts


def start_process_add_words_in_db(flag=False):
    """Запускает процесс добавления слов (Word) в базу данных"""

    data_set_with_words = _get_data_from_excel(
        'A:E',
        2000,
        'words',
    )
    if flag:
        _add_words_in_db(data_set_with_words)
        print('Импорт СЛОВ в базу завершен!')
        print(f'{Word.objects.filter(is_it=True).count()} - с флагом IT')
        print(f'{Word.objects.filter(is_popular=True).count()} - с флагом POPULAR')
    return data_set_with_words


def delete_all_words_in_db(flag=False):
    """Удаляет все слова в базе"""
    if flag:
        print(f'До удаления в базе данных было: {Word.objects.all().count()} слов')
        Word.objects.all().delete()

        print('Удаление завершено')
        print(f'Сейчас в базе данных: {Word.objects.all().count()} слов')


if __name__ == '__main__':
    # parts = start_process_add_parts_in_db(False)  # изменить аргумент на True для включения функции;
    # print(len(parts))
    delete_all_words_in_db(False)
    print()
    words = start_process_add_words_in_db(True)  # изменить аргумент на True для включения функции;
