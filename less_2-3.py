import yaml
"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""

data = {
    'white_wine': ['Chardonnay', 'Riesling', 'Sauvignon_Blanc'],
    'quantity': 6,
    'price': {
        'Chardonnay': '26\u20ac',
        'Riesling' : '15\u20ac-18\u20ac',
        'Sauvignon_Blanc' : '20\u20ac-22\u20ac'
    }
}

with open('file.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

with open('file.yaml', 'r', encoding='utf-8') as f:
    loading = yaml.load(f, Loader=yaml.SafeLoader)

print(data == loading)