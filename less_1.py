import subprocess
from chardet import detect

"""
1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате 
и проверить тип и содержание соответствующих переменных. Затем с 
помощью онлайн-конвертера преобразовать строковые представление в формат Unicode 
и также проверить тип и содержимое переменных.
"""

def remake(*args):
    for item in args:
        for word in item:
            print(f'{word} - {type(word)}')


strs = ['разработка', 'сокет', 'декоратор']

strs_unicode = [
    '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
    '\u0441\u043e\u043a\u0435\u0442',
    '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
]

remake(strs, strs_unicode)

"""
разработка - <class 'str'>
сокет - <class 'str'>
декоратор - <class 'str'>
разработка - <class 'str'>
сокет - <class 'str'>
декоратор - <class 'str'>
"""


"""
2. Каждое из слов «class», «function», «method» записать в байтовом типе без 
преобразования в последовательность кодов (не используя методы encode и decode) 
и определить тип, содержимое и длину соответствующих переменных.
"""

def remake_bytes(*args):
    for item in args:
        for word in item:
            print(f'{word} - {type(word)}')


byte_strs = [
    b'class',
    b'function',
    b'method',
]

remake_bytes(byte_strs)

"""
b'class' - <class 'bytes'>
b'function' - <class 'bytes'>
b'method' - <class 'bytes'>
"""

"""
3. Определить, какие из слов «attribute», 
«класс», «функция», «type» невозможно записать в байтовом типе.
"""

def is_byte_type(*args):
    for item in args:
        try:
            eval(f'b"{item}"')
        except SyntaxError:
            print(f'Слово "{item}" невозможно записать в байтовом типе')

new_strs = [
    'attribute',
    'класс',
    'функция',
    'type'
]

is_byte_type(*new_strs)

"""
Слово 'класс' невозможно записать в байтовом типе
Слово 'функция' невозможно записать в байтовом типе
"""

"""
4.Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового
представления в байтовое и выполнить обратное преобразование (используя методы 
encode и decode).
"""

def some_code(*args):
    for el in args:
        coding_el = el.encode('utf-8')
        print(
            f'Байтовое представление - {coding_el}, строковое представление - {coding_el.decode("utf-8")}')

words = [
    'разработка',
    'администрирование',
    'protocol',
    'standard',
]

some_code(*words)

"""
Байтовое представление - b'\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0', строковое представление - разработка
Байтовое представление - b'\xd0\xb0\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5', строковое представление - администрирование
Байтовое представление - b'protocol', строковое представление - protocol
Байтовое представление - b'standard', строковое представление - standard
"""

"""
5.Выполнить пинг веб-ресурсов yandex.ru, youtube.com и 
преобразовать результаты из байтовового в строковый тип на кириллице.
"""

def ping_webs(*args):
    for web in args:
        ping_out = subprocess.Popen(args=('ping', web), stdout=subprocess.PIPE)
        for line in ping_out.stdout:
            result = detect(line)['encoding']
            line = line.decode(result).encode('utf-8')
            print(line.decode('utf-8'))
            

webs = ['yandex.ru', 'youtube.com']

ping_webs(*webs)

"""
6. Создать текстовый файл test_file.txt, заполнить его тремя строками: 
«сетевое программирование», «сокет», «декоратор». Проверить кодировку 
файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести 
его содержимое.
"""

file = 'test-file.txt'

strs_line = [
    'сетевое программирование',
    'сокет',
    'декоратор',
]

with open(file, 'w') as f:
    for item in strs_line:
        f.write(f'{item}\n')

with open(file, 'rb') as f:
    print(f'Кодировка по умолчанию {detect(f.read())["encoding"]}')

with open(file, 'r', encoding='utf-8') as f:
    print(f.read())