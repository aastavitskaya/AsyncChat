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
        'Chardonnay': '26$',
        'Riesling' : '15$-18$',
        'Sauvignon_Blanc' : '20$-22$'
    }
}

with open('file.yuml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

with open('file.yuml', 'r', encoding='utf-8') as f:
    loading = yaml.load(f, Loader=yaml.SafeLoader)

print(data == loading)