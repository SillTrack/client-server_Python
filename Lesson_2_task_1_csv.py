# Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку
# определенных данных из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл
# в формате CSV. Для этого:
# Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, 
# их открытие и считывание данных. В этой функции из считанных данных необходимо 
# с помощью регулярных выражений извлечь значения параметров
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
# Значения каждого параметра поместить в соответствующий список. 
# Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. 
# В этой же функции создать главный список для хранения данных отчета — например, 
# main_data — и поместить в него названия столбцов отчета в виде списка:
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». 
# Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
# Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. 
# В этой функции реализовать получение данных через вызов функции get_data(),
# а также сохранение подготовленных данных в соответствующий CSV-файл;
# Проверить работу программы через вызов функции write_to_csv(). 

import csv
# import copy
import re



list_of_params = [ 'Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
list_of_files = ['info_1.txt', 'info_2.txt', 'info_3.txt']




def get_data(list_of_files):
    main_data = [ ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы'] ]
    for file in list_of_files:
        os_prod_list = []
        os_name_list = []
        os_code_list = []
        os_type_list = []
        list_of_lists = [os_prod_list, os_name_list, os_code_list, os_type_list]
        with open(file, 'r') as csv_file:
            iter = 0
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                result = re.split(r':', row[0])
                obj = result[1].lstrip() if (result[0] in list_of_params) else None
                if obj and (iter < len(list_of_params)):
                    list_of_lists[list_of_params.index(result[0])].append(obj)
                    iter += 1 
            main_data.append(
                [
                    os_prod_list[:1][0],
                    os_name_list[:1][0],
                    os_code_list[:1][0],
                    os_type_list[:1][0]
                ]
            )
    # main_data.append(list_of_lists)
    return main_data


def write_to_csv(file_name):
    with open(file_name, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        print(get_data(list_of_files))
        for row in get_data(list_of_files):
            csv_writer.writerow(row)


write_to_csv('new_test.csv')
