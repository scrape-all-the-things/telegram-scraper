import configparser
import json
import os
import logging


class TelegramConfig:
    def __init__(self):
        self.command = None
        self.command_on = None
        self.use_participant_fields = []
        self.use_full_userinfo_fields = []
        self.download_profile_photos = False
        self.telegram_phone = None
        self.telegram_api_id = 1234567
        self.telegram_api_hash = None
        self.log_level = logging.INFO
        self.log_format = None
        self.log_file = None

    def read_config_file(self, config_file):
        if not os.path.exists(config_file):
            print(f'ERROR: configuration file {config_file} not found! Read the README.md file for instructions')
            exit(66)

        config = configparser.RawConfigParser()
        config.read(config_file)

        for required_section in ['telegram', 'scraper', 'logging']:
            if not config.has_section(required_section):
                print(f'ERROR: configuration file {config_file} is missing the required [{required_section}] section')
                exit(66)

        self.command = config.get('action', 'command')
        self.command_on = config.get('action', 'on')

        self.use_participant_fields = json.loads(config.get('scraper', 'user_fields'))
        self.use_full_userinfo_fields = json.loads(config.get('scraper', 'extended_user_fields'))
        self.download_profile_photos = config.get('scraper', 'download_profile_photos', fallback=False)

        self.telegram_phone = config.get('telegram', 'phone')
        self.telegram_api_id = int(config.get('telegram', 'api_id'))
        self.telegram_api_hash = config.get('telegram', 'api_hash')

        if self.telegram_api_id == 1234567:
            print(f'Telegram api_id is set to the example value in {config_file}, please re-read the README.md')
            exit(66)

        self.log_level = logging.getLevelName(config.get('logging', 'level', fallback="INFO"))
        self.log_format = config.get('logging', 'format', fallback=None)
        self.log_file = config.get('logging', 'file', fallback=None)
