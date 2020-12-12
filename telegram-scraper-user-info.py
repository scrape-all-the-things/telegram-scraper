#!/usr/bin/env python3

# SCRAPE ALL THE THINGS
# Telegram scraper
# Version 0.1 alpha
# https://github.com/scrape-all-the-things/telegram-scraper

# Import ALL the libraries, well... maybe not ALL the libraries
import logging
import sys
from scraper import configuration, telegram

# Read and check configuration
config = configuration.TelegramConfig()
config.read_config_file('config.ini')

# Set up logging
logger = logging.getLogger('telegram_scraper')
logger.setLevel(config.log_level)
formatter = logging.BASIC_FORMAT
if config.log_format:
    formatter = logging.Formatter(config.log_format)
if config.log_file:
    fh = logging.FileHandler(filename=config.log_file, mode='a')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

# Check commandline arguments
if len(sys.argv) != 2:
    logger.error("Usage: ./telegram-scraper-user-infp.py <userid>")
    exit(1)

userid = sys.argv[1]

# Connect to the Telegram server
logger.info(f"Connecting to Telegram for phone '{config.telegram_phone}' api_id '{config.telegram_api_id}'")
telegram = telegram.Telegram()
telegram.connect(config.telegram_phone, config.telegram_api_id, config.telegram_api_hash)

# Check authorisation
if not telegram.is_user_authorized():
    logger.info("This program is not yet authorized, a code will be requested and sent to your Telegram account")
    logger.info("Enter this code on the stdin")
    telegram.request_authorization_code()
    telegram.verify_authorization_code(input("Please enter the code: "))

print(f'Fetching info for user id: {userid}')
userinfo = telegram.full_user_info(int(userid))

# Print out user info
for column in userinfo.user.__dict__.keys():
    print(f'\'{column}\': {getattr(userinfo.user, column)}')
