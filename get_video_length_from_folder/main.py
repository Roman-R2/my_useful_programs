"""
Данный скрипт собирает общее время проигрывания видеофайлов и колличество
найденных видеофайлов из указанной папке INSPECT_DIR, проходя по всем
подпапкам и выбирая только файлы с форматом, указанным в ALLOWED_FORMATS

Для работы требуется библиотека MediaInfo (https://mediaarea.net/en/MediaInfo)

"""
from datetime import datetime, timedelta, time
import os
from pprint import pprint

from pymediainfo import MediaInfo

INSPECT_DIR = r"C:\Users\Admin\Desktop\Обучающие видео по IT\Python\[WebForMySelf] Django. Полное руководство (2020)"

ALLOWED_FORMATS = (".mp4", ".avi")


def test(file):
    media_info = MediaInfo.parse(file)
    for track in media_info.tracks:
        if track.track_type == "Audio":
            print("Track data:")
            pprint(track.other_duration[4])
    return True


def get_playing_time_for_file(file, type='Video'):
    """
    Функция возвращает время воспроизведения файла заданого типа
    в парамере type
    Может вернуть None, если в файле нет дорождки видео,
    если ищутся видео, или аудио, если ищутся аудио данные
    type может быть строкой со значением Video или Audio
    Пример возвращаемого значения строка: "00:04:19:14"

    """

    media_info = MediaInfo.parse(file)
    for track in media_info.tracks:
        if track.track_type == type:
            return track.other_duration[4]


def convert_str_to_time(string):
    """
    Функция преобразует строку в формате HH:MM:SS:ff в объект datetime

    """
    if string is None:
        return time(0, 0)
    string = string.replace(";", ":")
    return datetime.strptime(string, "%H:%M:%S:%f").time()


def sum_files_times_in_folder(folder, allowed_formats_list):
    """"
    Функция проходит по переданной директории folder и смотрит,
    подходит ли формат файла из списка allowed_formats_list
    для каждого найденного файла, если подходит,
    то берет его время в формате datetime и суммирует его с общим временем.
    Возвращает список из следующих параметров:
        files_count     - сумма найденных видеофайлов
        all_video_time  - общее время видеофайлов
    """
    files_count = 0
    all_video_time = timedelta(hours=0,
                               minutes=0,
                               seconds=0,
                               microseconds=0
                               )
    for dirs, folder, files in os.walk(folder):
        for el in files:
            if os.path.splitext(el)[-1] in allowed_formats_list:
                path_to_videos = f"{dirs}/{el}".replace("\\", "/")
                videofile_time = convert_str_to_time(
                    get_playing_time_for_file(path_to_videos))
                print(f"Время: {str(videofile_time)}   файла: {el}")
                all_video_time = all_video_time + timedelta(
                    hours=videofile_time.hour,
                    minutes=videofile_time.minute,
                    seconds=videofile_time.second,
                    microseconds=videofile_time.microsecond
                )
                files_count += 1
    return files_count, all_video_time


print(test(
    r"C:/Users/Admin/Desktop/Обучающие видео по IT/Английский язык/"
    r"Мария Батхан - Училка первая моя (2019)/Неделя 3/7/1.mp4"))

rez_list = sum_files_times_in_folder(INSPECT_DIR, ALLOWED_FORMATS)
scaning_folder = INSPECT_DIR
scaning_folder = scaning_folder.split('\\')[-1]
print(
    "--------------------------------------------------\n"
    f"Сканированная папка: {scaning_folder}\n"
    f"Файлов найдено: {rez_list[0]}\n"
    f"Общее время: {rez_list[1]}")
