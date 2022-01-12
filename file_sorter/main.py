"""
Author: Roman Slyusar (https://github.com/Roman-R2)

Сортировщик файлов (например фотографий)
Проблематика: скопилось много папок с фотографиями, в том числе и копий
фотографий на разных дисках, скопированных с нескольких независимых
источников в разное время.
Требования:
1. Отсортировать файлы по датам:
    -. Определить разрешенные форматы и исходную папку.
    а. Пройтись по файлам и подпапкам в указанной папке.
    б. Исключить дублирование фотографий
    в. Для каждого разрешенного формата создать отдельную папку
    г. Положить копии файлов в папку, в названии которой будет указана
    дата файла.
    д. Вывести статистику работы программы
"""

import os
import shutil
import time
from tqdm import tqdm

from datetime import datetime

# Папка с исходными, неотсортированными файлами
UNSORTED_FOLDER = r"C:\Users\Admin\Desktop\test_photo"

# Папка для результата выполнения скрипта
TARGET_FOLDER = r"C:\Users\Admin\Desktop\test_photo_sorted"
# Разрешенные для сортировки форматы
ALLOWED_FORMATS = (
    '.jpg',
    # '.mp4',
)


def get_file_id(create_date, bytes_size) -> str:
    """Вернет уникальный идентификатор для файла"""
    return f"{create_date.strftime('%Y%m%d%H%M%S')}{bytes_size}"


def get_data_folder_name(file_create_date) -> str:
    """Вернет строку для имени папки, содержащей дату создания фала"""
    return file_create_date.strftime('%Y-%m-%d')


def str_to_time(str_time: str):
    return datetime.strptime(str_time, '%a %b %d %H:%M:%S %Y')


class PhotoSorter:
    def __init__(
            self,
            unsorted_folder: str,
            target_folder: str,
            allowed_formats: tuple
    ):
        self._unsorted_folder = unsorted_folder
        self._target_folder = target_folder
        self._allowed_formats = allowed_formats
        self.__unprocessed_files = []
        self.__duplicate_files = []
        self.__shadow_folder_struct = {}

    def start(self):
        """
        Главный метод-обработчик
        :return: None
        """
        self._prepare_folder()
        self._prepare_files_for_statistics()
        self._walk_the_files()
        self._store_stat_duplicate_files()
        self._store_stat_unprocessed_files()
        self._say_end()

    def _prepare_files_for_statistics(self):
        """Подготовит новые файлы для статистики или очистит пред идущие"""
        with open(
                os.path.join(self._target_folder, 'stat_duplicate_files.txt'),
                'w'
        ) as fd:
            pass
        with open(
                os.path.join(self._target_folder,
                             'stat_unprocessed_files.txt'),
                'w'
        ) as fd:
            pass

    def _store_stat_duplicate_files(self):
        """Сохранит информацию о найденных дубликатах файлов в специальный
        файл статистики"""
        self._add_info_to_file(
            filename='stat_duplicate_files.txt',
            list_of_files=self.__duplicate_files,
            default_str='Дубликатов файлов не найдено...'
        )

    def _store_stat_unprocessed_files(self):
        """Сохранит информацию о найденных дубликатах файлов в специальный
        файл статистики"""
        self._add_info_to_file(
            filename='stat_unprocessed_files.txt',
            list_of_files=self.__unprocessed_files,
            default_str='Нет необработанных файлов...'
        )

    def _add_info_to_file(
            self,
            filename: str,
            list_of_files: list,
            default_str: str = '---'
    ):
        """Сохранит информацю о статистике в указанный файл."""
        with open(
                os.path.join(self._target_folder, filename),
                'a'
        ) as fd:
            if not self.__duplicate_files:
                fd.writelines(default_str)
            else:
                for count, file in enumerate(list_of_files, start=1):
                    fd.writelines(f'{count}.\t{file}\n')

    def _say_end(self):
        """Выведет сообщение об окончании работы"""
        print(f"-----------------------------------------------------------")
        print(f"---------- Сортировка файлов окончена! --------------------")
        print(f"-----------------------------------------------------------")

    def _prepare_folder(self):
        """
        Подготовит структуру папок в папке вывода результата
        """
        # Если папка существует, то удалим ее со всеми вложенными файлами
        if os.path.exists(self._target_folder):
            shutil.rmtree(self._target_folder)
        # Создадим папку и структуру подпапок заново
        os.mkdir(self._target_folder)
        for file_format in self._allowed_formats:
            os.mkdir(os.path.join(self._target_folder, file_format))
            self.__shadow_folder_struct[file_format] = {}
        print("Структура папок подготовлена.")

    def _walk_the_files(self):
        """Пройдется по файлам в заданной папке"""

        for root, dirs, files in os.walk(self._unsorted_folder):
            if files:
                print(f"Обработка папки {root}")
                time.sleep(1)
                for file in tqdm(files):
                    full_path_to_file = os.path.join(root, file)
                    filename, file_extension = os.path.splitext(
                        full_path_to_file)
                    file_extension = file_extension.lower()
                    if file_extension in self._allowed_formats:
                        self._process_file(full_path_to_file, file_extension)
                    else:
                        self.__unprocessed_files.append(full_path_to_file)

    def _show_unprocessed_files(self):
        """Выведет в консоль файлы, которые не подошли по формату"""
        if not self.__unprocessed_files:
            print("Все файлы были обработаны...")
        else:
            print("Не обработанные фалы: ")
            for count, file in enumerate(self.__unprocessed_files, start=1):
                print(f"\t{count}. {file}")

    def _show_duplicate_files(self):
        """Выведет в консоль файлы, которые оказались идентичны уже
        скопированным в папку файлам по ряду параметров (дата создания и
        размер)"""
        if not self.__duplicate_files:
            print("Дубликатов файлов не найдено...")
        else:
            print("Дубликаты фалов: ")
            for count, file in enumerate(self.__duplicate_files, start=1):
                print(f"\t{count}. {file}")

    def _process_file(self, full_path_to_file, file_extension):
        """Обработает файл в соответствии с логикой"""

        file_creation_time = str_to_time(
            time.ctime(os.path.getmtime(full_path_to_file))
        )
        file_size_in_bytes = os.path.getsize(full_path_to_file)
        folder_name_for_file = get_data_folder_name(file_creation_time)
        folder_for_save = os.path.join(
            self._target_folder,
            file_extension,
            folder_name_for_file
        )
        # Создадим папку для файла, если ее еще нет
        if not os.path.exists(folder_for_save):
            os.mkdir(folder_for_save)
            # Запишем папку в структуру для сравнения файлов
            self.__shadow_folder_struct[file_extension][
                folder_name_for_file
            ] = []

        # Получим уникальный ключ файла
        file_id = get_file_id(
            file_creation_time,
            file_size_in_bytes
        )
        # Проверим файл на идентичность уже скопированным файлам по ряду
        # параметров (дата создания и размер)
        if file_id not in self.__shadow_folder_struct[file_extension][
            folder_name_for_file]:
            # Добавим идентификатор файла в структуру для сравнения
            self.__shadow_folder_struct[file_extension][
                folder_name_for_file].append(file_id)
            # Скопируем файл с его атрибутами в нужную папку
            shutil.copy2(full_path_to_file, folder_for_save)
        else:
            # Добавим файл в список дубликатов
            self.__duplicate_files.append(full_path_to_file)


if __name__ == '__main__':
    photo_sorter_obj = PhotoSorter(
        UNSORTED_FOLDER,
        TARGET_FOLDER,
        ALLOWED_FORMATS
    )
    photo_sorter_obj.start()
