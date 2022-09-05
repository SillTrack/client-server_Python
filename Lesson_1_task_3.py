def TryByte(statement):
    try:
        statement_byte = bytes(statement, encoding='utf-8')
        message = f"{statement} can be converted into bytes\n {statement_byte} has a type of {type(statement_byte)}"
    except:
        message = f"{statement} can`t be converted into bytes"
    print(message)
    return 0


list_of_words = ['attribute', 'type', 'класс', 'функция']
for word in list_of_words:
    TryByte(word)

# С помшью функции bytes() можно преобразовать все 4 слова, используя b'' не получится преобразовать
# слова на русском так как выдается ошибка SyntaxError, которая указывает что необходимо использовать
# только те символы которые содержаться в таблице ASCII. При использовании bytes мы явно указываем кодировку
# которую нужно перевести в байты

try:
    classbyte = b'класс'
finally:
    print(f"класс нельзя перевести в байты с помошью b'класс'")


