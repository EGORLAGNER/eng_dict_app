import pandas as pd
from dict.models import Word, WordStatistics
from account.models import User
from django.db.utils import IntegrityError

USER = User.objects.get(custom_id=1716285847555)

PATH_EXCEL_FILE = 'D:\\MAIN\\MY\\ENG\\my_dict.xlsx'


class DataImportHandler:
    def _check_value_is_string(self, *args):
        """Возвращает True, если переданное значение является строкой"""
        for value in args:
            if isinstance(value, str):
                return True
            else:
                return False

    def _check_value_is_bool(self, *args):
        """Возвращает True, если переданное значение является логическим"""
        for value in args:
            if isinstance(value, bool):
                return True
            else:
                return False

    def _get_data_from_excel(self, columns_range, rows_range, sheet_name):
        """Возвращает список со словарями, которые содержат данные:
            ключ - название ячейки;
            значение - значение ячейки;

        Аргументы:
            columns_range - str, диапазон колонок для чтения, например 'A:F'
            rows_range - int, номер строки, до которой читать файл, например 1000.
            sheet_name - str, название страницы в excel файле, например 'words'

        Excel файл должен лежать рядом с данным python файлом."""

        file_path = PATH_EXCEL_FILE

        # Прочитать данные с указанной страницы в DataFrame
        df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=columns_range, nrows=rows_range)

        # Преобразовать DataFrame в словарь
        list_with_dicts = df.to_dict(orient='records')

        # data_dict теперь содержит данные в формате словаря
        return list_with_dicts

    def _add_words_in_db(self, list_with_dict):
        """Добавляет в базу данных части речи (Word)"""
        count_add_words = 0
        for dictionary in list_with_dict:
            eng = dictionary['eng']
            rus = dictionary['rus']

            print(f'тип:{type(rus)}, значение: {rus}')
            if isinstance(rus, float):
                rus = None

            try:
                if self._check_value_is_string(eng) and rus is not None:
                    user = USER
                    obj_statistics = WordStatistics.objects.create(slug=str(user.custom_id) + '_' + eng)
                    user.words.create(eng=eng, rus=rus, statistics=obj_statistics)

                    Word.objects.create(
                        eng=eng.lower(),
                        rus=rus,
                        user=user
                    )
                    print('добавлено')
                    count_add_words = count_add_words + 1
                else:
                    print('пропущено')
                    continue
            except IntegrityError:
                print('except IntegrityError')
                continue

        print(f'Добавлено слов в базу: {count_add_words}')
        print(f'Всего слов в базе: {Word.objects.all().count()}')

    def start_process_add_words_in_db(self, flag=False):
        """Запускает процесс добавления слов (Word) в базу данных"""

        data_set_with_words = self._get_data_from_excel(
            'A:E',
            2000,
            'words',
        )
        if flag:
            self._add_words_in_db(data_set_with_words)
            print('Импорт СЛОВ в базу завершен!')
        return data_set_with_words

    def delete_all_words_in_db(self, flag=False):
        """Удаляет все слова в базе"""
        if flag:
            print(f'До удаления в базе данных было: {Word.objects.all().count()} слов')
            Word.objects.all().delete()

            print('Удаление завершено')
            print(f'Сейчас в базе данных: {Word.objects.all().count()} слов')


if __name__ == '__main__':
    handler = DataImportHandler()
    handler.delete_all_words_in_db()
    handler.start_process_add_words_in_db()  # изменить аргумент на True для включения функции;
