from chardet import detect
import re
import csv
"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл
"""

def get_data(*args):

    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = [
        ['Изготовитель системы',
        'Название ОС',
        'Код продукта',
        'Тип системы',]
    ]
    for file in args:
        with open(file, 'rb') as f:
            codec = detect(f.read())["encoding"]
  
        with open(file, 'r', encoding=codec) as f:
            data = f.read()

            os_prod_list.append(
                re.search(r'(Изготовитель системы:)(\s{2,})([\S].*)', data).group(3)
            )
            os_name_list.append(
                re.search(r'(Название ОС:)(\s{2,})([\S].*)', data).group(3)
            )
            os_code_list.append(
                re.search(r'(Код продукта:)(\s{2,})([\S].*)', data).group(3)
            )
            os_type_list.append(
                re.search(r'(Тип системы:)(\s{2,})([\S].*)', data).group(3)
            )
    for prod, name, code, types in zip(
        os_prod_list,
        os_name_list,
        os_code_list,
        os_type_list
    ):
        main_data.append([prod, name, code, types])
    
    return main_data

def write_to_csv(csv_fl, *args):
    with open(csv_fl, 'w',  encoding='utf-8') as f:
        f_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        f_writer.writerows(get_data(*args))


    files = [
        'info_1.txt',
        'info_2.txt',
        'info_3.txt',
    ]

    write_to_csv("data_file.csv", *files)

