import configparser

config = configparser.ConfigParser()
print(config.read('../env_local.ini'))
print(config.sections())