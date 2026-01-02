
import json
import base64

# Исходный JSON
json_data = {"size": "L", "color": "blue"}

# Преобразуем в строку и затем в бинарный формат
json_str = json.dumps(json_data)
print(json_str)
binary_data = json_str.encode('utf-8')

# Если нужно, можно закодировать в Base64 для сохранения в текстовом формате
encoded_data = base64.b64encode(binary_data).decode('utf-8')
print(binary_data)
print(encoded_data)

