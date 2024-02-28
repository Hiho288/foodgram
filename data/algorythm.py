import json

# Чтение данных из исходного JSON-файла
with open('ingredients.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Создание пустого списка для преобразованных данных
transformed_data = []

# Преобразование данных
for index, item in enumerate(data, start=1):
    transformed_item = {
        "model": "api.Ingredient",
        "pk": index,
        "fields": {
            "name": item["name"],
            "measurement_unit": item["measurement_unit"]
        }
    }
    transformed_data.append(transformed_item)

# Сохранение преобразованных данных в новый JSON-файл
with open('ingredients_right.json', 'w', encoding='utf-8') as f:
    json.dump(transformed_data, f, indent=2, ensure_ascii=False)
