import argparse
import json
import os


class ConfigurationError(Exception):
    pass


def load_file_config(config_file_path):
    if not os.path.exists(config_file_path):
        raise ConfigurationError(f"Config file {config_file_path} not found")

    with open(config_file_path) as config_file:
        config = json.load(config_file)

    return config


def load_config(config_file_path, required_params):
    # Загрузка конфигурации из файла
    config_dict = load_file_config(config_file_path)

    # Попытка взять параметры из переменных среды, если они есть
    for param in required_params:
        config_dict[param] = os.getenv(param.upper()) or config_dict.get(param)

    # Проверка наличия всех обязательных параметров
    for param in required_params:
        if not config_dict.get(param):
            raise ConfigurationError(f"Parameter {param} is missing or empty")

    return config_dict
