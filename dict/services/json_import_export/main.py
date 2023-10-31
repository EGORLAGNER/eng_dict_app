from django.contrib.auth.models import User
from dict.models import Word
import json
from config.settings import PATH_JSON_FILE

JSON_BACKUP_FILE = PATH_JSON_FILE


def get_all_words_in_db():
    """Возвращает списком все слова из базы данных, которые связаны с конкретным пользователем."""

    user = User.objects.get(id=1)
    word = user.word_set.all().values()
    return list(word)


def json_export_in_file(data, path):
    # Имя файла, в который мы сохраним данные
    path_file = path

    # Открываем файл для записи в режиме записи (mode="w")
    with open(path_file, "w") as json_file:
        # Используем функцию json.dump() для записи данных в файл
        json.dump(data, json_file)

    print(f"Данные сохранены в файл {path_file}")
    print(f"В файле всего: {len(data)} слов")


def json_import_from_file(path):
    # Имя файла, из которого мы будем читать данные
    path_file = path

    # Открываем файл для чтения в режиме чтения (mode="r")
    with open(path_file, "r") as json_file:
        # Используем функцию json.load() для чтения данных из файла
        data = json.load(json_file)

    # Теперь данные из файла хранятся в переменной data и могут быть использованы
    print("Прочитанные данные из файла:")
    return data


def add_words_in_db(list_with_dict):
    """Добавляет в базу данных слова (Word)"""
    count_add_words = 0
    for dictionary in list_with_dict:
        eng = dictionary['eng']
        rus = dictionary['rus']

        description = dictionary['description']
        rating = dictionary['rating']

        is_popular = dictionary['is_popular']
        is_it = dictionary['is_it']
        is_visible = dictionary['is_visible']

        slug = dictionary['slug']

        Word.objects.create(
            eng=eng.lower(),
            rus=rus.lower(),

            description=description,
            rating=rating,

            is_popular=is_popular,
            is_it=is_it,
            is_visible=is_visible,

            slug=slug,

            user_id=1
        )
        print('добавлено')
        count_add_words = count_add_words + 1

    print(f'Добавлено слов в базу: {count_add_words}')
    print(f'Всего слов в базе: {Word.objects.all().count()}')


def save_backup_json(flag=False):
    if flag:
        words = get_all_words_in_db()
        json_export_in_file(words, JSON_BACKUP_FILE)


def load_backup_json(flag=False):
    if flag:
        words = json_import_from_file(JSON_BACKUP_FILE)
        add_words_in_db(words)


if __name__ == '__main__':
    save_backup_json()   # передать True, чтобы активировать;
    load_backup_json()   # передать True, чтобы активировать;
