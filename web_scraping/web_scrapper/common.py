import yaml

__config = None

def config():
    global __config
    if not __config:
        with open('config.yaml', 'r') as file_:
            __config = yaml.full_load(file_)

    return __config