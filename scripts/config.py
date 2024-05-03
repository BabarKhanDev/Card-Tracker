import configparser


def read_config(config_location: str = "config.ini") -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(config_location)
    return config


def get_tcg_api_key(config_location: str = "config.ini") -> str:
    config = configparser.ConfigParser()
    config.read(config_location)
    return config["pokemontcg"]["API_key"]


def write_config(config: configparser.ConfigParser, config_location: str = "config.ini") -> None:
    with open(config_location, 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    print(read_config("../config.ini")["pokemontcg"]["API_key"])