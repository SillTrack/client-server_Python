# Создать текстовый файл test_file.txt, заполнить его тремя строками:
# «сетевое программирование», «сокет», «декоратор».
# Проверить кодировку файла по умолчанию. Принудительно открыть файл
# в формате Unicode и вывести его содержимое.


with open('test_file.txt', 'r') as test_file:
    print(test_file.encoding)

try:
    with open('test_file.txt', 'rt', encoding='ascii', ) as test_file:
        for line in test_file:
            print(line)
except UnicodeDecodeError:
    print('Открыть в ascii нельзя')

try:
    with open('test_file.txt', 'rt', encoding='utf-8', ) as test_file:
        for line in test_file:
            line_read = line.decode('cp866').encode('utf-8')
            print(line.decode('utf-8'))
except UnicodeDecodeError:
    print('Открыть в utf-8 нельзя')

with open('test_file.txt', 'rt', encoding='utf8', errors='replace') as test_file:
    print(test_file.read())
