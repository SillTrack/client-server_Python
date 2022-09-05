# Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
# преобразовать результаты из байтовового в строковый тип на кириллице.
import subprocess
args = [['ping', 'youtube.com'],['ping', 'yandex.ru'] ]
for argument in args:   
    subproc_ping = subprocess.Popen(argument, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        line = line.decode('cp866').encode('utf-8')
        print(line.decode('utf-8'))

# необходимо декодировать полученную информацию, потому что декодер UTF-8 может сгенерировать исключение, так как байтовое значение 
# пришедшее с ресурса может является некорректным в этой кодировке. Это происходит из-за того, что выводимое в результате
# работы модуля subprocess сообщение было закодировано не с помощью UTF-8. Во избежание
# ошибок и кодирование, и декодирование данных следует выполнять в одной кодировке — UTF-8.
