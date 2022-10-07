# Есть файл orders в формате JSON с
# информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными. Для
# этого:
# a. Создать функцию write_order_to_json(), в которую передается 5 параметров — товар
# (item), количество (quantity), цена (price), покупатель (buyer), дата (date). Функция
# должна предусматривать запись данных в виде словаря в файл orders.json. При
# записи данных указать величину отступа в 4 пробельных символа;
# b. Проверить работу программы через вызов функции write_order_to_json() с передачей
# в нее значений каждого параметра.
import json

def write_order_to_json(item, quantity, price, buyer, date):
    try:
        with open ('orders.json', 'r') as json_file:
            try:
                orders_file = json.load(json_file)
            except json.decoder.JSONDecodeError:
                raise Exception('Файл пустой')           
            if not 'orders' in orders_file:
                orders_file['orders'] = []
            orders_file['orders'].append({
                'item': item,
                'quantity': quantity,
                'price': price,
                'buyer': buyer,
                'date': date
            })
    except FileNotFoundError:
        raise Exception('Файл не найден в выбранной директории')
    with open ('orders.json', 'w') as json_file:
        json.dump(orders_file, json_file, indent=4)

for i in range(8):
    write_order_to_json(f'Product№{i}', 2*i, 120*i, 'Ivan', '09-09-2021')

# при использовании знака № отображается не он а \u2116