import os
import configparser


class Config(object):

    def __init__(self, config_location=None):
        self.config = configparser.ConfigParser()
        if not config_location:
            config_location = os.environ.get("SETTINGS_FILE", "./config.ini")

        self.config.read(config_location)

    def get_config(self):
        return self.config
