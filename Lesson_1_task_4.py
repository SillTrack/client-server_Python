# Преобразовать слова «разработка», «администрирование», «protocol»,
# «standard» из строкового представления в байтовое
# и выполнить обратное преобразование (используя методы encode и decode).

list_of_words = ["разработка", "администрирование", "protocol", "standard"]
for word in list_of_words:
    word = word.encode('utf-8')
    print(word)
    word = word.decode('utf-8')
    print(word)
