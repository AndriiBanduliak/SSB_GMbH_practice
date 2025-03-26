import json

def prettify_json_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Пытаемся загрузить весь файл как один JSON-объект
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print("Не удалось загрузить файл как единый JSON-объект, пробую построчное чтение...")
        # Если ошибка, пробуем разобрать файл построчно (например, JSON Lines)
        data = []
        for i, line in enumerate(content.splitlines(), 1):
            if line.strip():
                try:
                    obj = json.loads(line)
                    data.append(obj)
                except json.JSONDecodeError as line_err:
                    print(f"Ошибка при обработке строки {i}: {line_err}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Файл {output_file} успешно создан!")

if __name__ == '__main__':
    input_file = "messages.json"
    output_file = "messages_pretty.json"
    prettify_json_file(input_file, output_file)
