from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (ChannelParticipant, ChannelParticipantAdmin,
                               ChannelParticipantCreator,
                               ChannelParticipantSelf, InputPeerEmpty,
                               UserStatusEmpty,
                               UserStatusLastMonth, UserStatusLastWeek,
                               UserStatusOffline, UserStatusOnline,
                               UserStatusRecently, ChatForbidden, User, Channel, Chat, ChannelForbidden)


class Telegram:
    USER_TYPE_ADMIN = 'admin'
    USER_TYPE_CREATOR = 'creator'
    USER_TYPE_PARTICIPANT = 'participant'
    USER_TYPE_SELF = 'myself'
    USER_TYPE_UNKNOWN = 'unknown'

    USER_STATUS_EMPTY = ''
    USER_STATUS_RECENTLY = 'recently'
    USER_STATUS_ONLINE = 'online'
    USER_STATUS_OFFLINE = 'offline'
    USER_STATUS_LAST_WEEK = 'last week'
    USER_STATUS_LAST_MONTH = 'last month'
    USER_STATUS_UNKNOWN = 'unknown'

    _client: TelegramClient = None
    phone_number: str = None
    _api_id: int = None
    _api_hash: str = None
    _me: User = None

    def connect(self, phone_number, api_id, api_hash):
        self.phone_number = phone_number
        self._api_id = api_id
        self._api_hash = api_hash

        self._client = TelegramClient(phone_number, api_id, api_hash)
        self._client.connect()
        self._me = self._client.get_me()

    def list_channels(self, only_admin=False, list_from_date=None, limit_size=200):
        channels = []
        result = []

        dialogs_result = self._client(GetDialogsRequest(
            offset_date=list_from_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=limit_size,
            hash=0
        ))
        channels.extend(dialogs_result.chats)

        for channel in channels:
            if not isinstance(channel, Chat) \
                    and not isinstance(channel, ChannelForbidden) \
                    and not isinstance(channel, ChatForbidden):
                # List all channels or only channels for which we have admin privileges
                if not only_admin or channel.admin_rights or channel.creator:
                    result.append(channel)

        return result

    def list_groups(self, list_from=None, limit_size=200):
        groups = []
        chats_result = []

        result = self._client(GetDialogsRequest(
            offset_date=list_from,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=limit_size,
            hash=0
        ))
        groups.extend(result.chats)

        for group in groups:
            if not isinstance(group, ChatForbidden) and not isinstance(group, ChannelForbidden):
                if hasattr(group, 'megagroup') and group.megagroup:
                    chats_result.append(group)

        return chats_result

    @staticmethod
    def channel_participant_type(channel_participant):
        if isinstance(channel_participant, ChannelParticipant):
            return Telegram.USER_TYPE_PARTICIPANT
        elif isinstance(channel_participant, ChannelParticipantCreator):
            return Telegram.USER_TYPE_CREATOR
        elif isinstance(channel_participant, ChannelParticipantAdmin):
            return Telegram.USER_TYPE_ADMIN
        elif isinstance(channel_participant, ChannelParticipantSelf):
            return Telegram.USER_TYPE_SELF
        else:
            return Telegram.USER_TYPE_UNKNOWN

    @staticmethod
    def identify_user_status(channel_participant):
        user_status = channel_participant.status

        if isinstance(user_status, UserStatusEmpty) or user_status is None:
            return Telegram.USER_STATUS_EMPTY
        elif isinstance(user_status, UserStatusRecently):
            return Telegram.USER_STATUS_RECENTLY
        elif isinstance(user_status, UserStatusOnline):
            return Telegram.USER_STATUS_ONLINE
        elif isinstance(user_status, UserStatusOffline):
            return Telegram.USER_STATUS_OFFLINE
        elif isinstance(user_status, UserStatusLastWeek):
            return Telegram.USER_STATUS_LAST_WEEK
        elif isinstance(user_status, UserStatusLastMonth):
            return Telegram.USER_STATUS_LAST_MONTH
        else:
            return Telegram.USER_STATUS_UNKNOWN

    def full_user_info(self, user_id):
        return self._client(GetFullUserRequest(user_id))

    def is_user_authorized(self):
        return self._client.is_user_authorized()

    def request_authorization_code(self):
        self._client.send_code_request(self.phone_number)

    def verify_authorization_code(self, authorization_code):
        self._client.sign_in(self.phone_number, authorization_code)

    def get_channel_participants(self, target_group):
        return self._client.get_participants(target_group, aggressive=True)

    def download_profile_photo(self, user, to_file):
        return self._client.download_profile_photo(user, to_file)
