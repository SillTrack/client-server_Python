# Каждое из слов «class», «function», «method» записать в байтовом
# типе без преобразования в последовательность кодов 
# (не используя методы encode и decode) и определить тип,
# содержимое и длину соответствующих переменных.

class_byte = b'class'
function_byte = b'function'
method_byte = b'method'

print(class_byte)
print(function_byte)
print(method_byte)

print(type(class_byte))
print(type(function_byte))
print(type(method_byte))

print(len(class_byte))
print(len(function_byte))
print(len(method_byte))
