#!/usr/bin/env python3

# SCRAPE ALL THE THINGS
# Telegram scraper
# Version 0.1 alpha
# https://github.com/scrape-all-the-things/telegram-scraper

# Import ALL the libraries, well... maybe not ALL the libraries
import csv
import logging
import os
import time
from datetime import datetime
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

print('Scrape members for which group?')
groups = telegram.list_groups()
for group_nr in range(0, len(groups)):
    print('[' + str(group_nr) + ']' + ' - ' + groups[group_nr].title)

print()
g_index = input("Enter the group number: ")
target_group = groups[int(g_index)]

print()
download_profile_photos = input("Download profile pictures (y/N): ") == 'y'

print()
scrape_extended_userinfo = input("Extended user info scrape (will take MUCH longer, >1sec / user) (y/N): ") == 'y'

# Specify output file
outfile = "members_" + str(target_group.id) + "_" + datetime.now().strftime("%Y%m%d"
                                                                            "%H%M%S") + ".csv"

logger.info(f'Requesting participant list for {target_group.title}')
time.sleep(1)
all_participants = telegram.get_channel_participants(target_group)
logger.info(f'Fetched {len(all_participants)} participants for {target_group.title}')

logger.info(f'Saving to file {outfile}...')
time.sleep(1)
with open(outfile, "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")

    firstRow = True
    columns = []
    for user in all_participants:
        # Request additional info from the server (takes a LONG time)
        full_info = telegram.full_user_info(user.id) if scrape_extended_userinfo else None

        # What group is this user in
        if firstRow:
            columns.append("group")
        values = [target_group.title]

        for column in config.use_participant_fields:
            if firstRow:
                columns.append(column)

            # What kind of participant is the user
            if column == "participant":
                channelParticipant = getattr(user, column)
                participantType = telegram.channel_participant_type(channelParticipant)

                values.append(participantType)

                # When did the user become a member and if admin, who made him admin
                if firstRow:
                    columns.append("participant_since")
                    columns.append("participant_promoted_by")

                values.append("" if participantType == telegram.USER_TYPE_CREATOR else channelParticipant.date)
                values.append(
                    str(channelParticipant.promoted_by) if participantType == telegram.USER_TYPE_ADMIN else "")

            # When was the user last online
            elif column == "status":
                statusObject = getattr(user, column)
                userStatus = telegram.identify_user_status(user)

                if userStatus == telegram.USER_STATUS_ONLINE:
                    value = datetime.now()
                elif userStatus == telegram.USER_STATUS_OFFLINE:
                    value = statusObject.was_online
                else:
                    value = userStatus

                values.append(value)

            # Retrieve user profile image
            elif column == "photo":
                value = getattr(user, column)
                filename = f"profile_pics_{target_group.id}/{user.id}.jpg"
                if value is not None and download_profile_photos:
                    path = telegram.download_profile_photo(user, to_file=filename)
                    values.append(path)
                else:
                    # If the file exists from a previous run, include that
                    if os.path.exists(filename):
                        values.append(filename)
                    else:
                        values.append("")

            # Include these fields that don't need special treatment like the ones above
            elif column in config.use_participant_fields:
                value = getattr(user, column)
                values.append(value if value is not None else "")

        # Process the extended userinfo fields
        if scrape_extended_userinfo:
            for userinfo_field in config.use_full_userinfo_fields:
                if firstRow and not userinfo_field == "profile_photo":
                    columns.append(userinfo_field)

                value = getattr(full_info, userinfo_field)
                if userinfo_field == "profile_photo":
                    if firstRow:
                        columns.append("profile_photo_date")

                    value = value.date if value is not None else ""

                values.append(value)

        if firstRow:
            writer.writerow(columns)
            firstRow = False

        writer.writerow(values)

logger.info(f'Member list for group {target_group.title} scraped and saved {len(all_participants)} to {outfile}.')
