import pandas as pd
from core.models import Word, Part

EXCEL_DATA_FILE = 'C:\\Users\\LAGNER\\PycharmProjects\\eng_dict_app\\data_file.xlsx'


def _check_is_string(*args):
    """Возвращает True, если переданное значение не является строкой"""
    for value in args:
        if not isinstance(value, str):
            return True


def _check_is_bool(*args):
    """Возвращает True, если переданное значение не является строкой"""
    for value in args:
        if not isinstance(value, bool):
            return True


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
    for dictionary in list_with_dict:
        eng = dictionary['eng']
        rus = dictionary['rus']
        is_popular = dictionary['popular']
        if is_popular == 'true' or 'True':
            is_popular = True
        else:
            is_popular = False

        if _check_is_string(eng, rus) or _check_is_bool(is_popular):
            continue

        else:
            Word.objects.create(
                eng=eng.lower(),
                rus=rus.lower(),
                is_popular=is_popular,
            )
            print('yes')


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
        'A:D',
        1000,
        'words',
    )
    if flag:
        _add_words_in_db(data_set_with_words)
        print('Импорт СЛОВ в базу завершен!')
    return data_set_with_words


if __name__ == '__main__':
    parts = start_process_add_parts_in_db(False)  # изменить аргумент на True для включения функции;
    words = start_process_add_words_in_db(False)  # изменить аргумент на True для включения функции;
