import configparser


class Config(object):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("./config.ini")

    def get_config(self):
        return self.config


config = Config().get_config()
