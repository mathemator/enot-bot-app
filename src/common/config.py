import json
from os.path import exists


class ConfigurationError(Exception):
    pass


def load_config(config_file_path, required_params):
    if not exists(config_file_path):
        raise ConfigurationError(f"Config file {config_file_path} not found")

    with open(config_file_path) as config_file:
        config = json.load(config_file)

    for param in required_params:
        if param not in config or not config[param]:
            raise ConfigurationError(
                f"Parameter {param} is missing or empty in the config file"
            )

    return config
