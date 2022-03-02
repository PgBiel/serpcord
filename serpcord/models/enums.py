from enum import Flag, Enum

from .model_abc import StrEnumAPIModel, IntEnumAPIModel, FlagEnumAPIModel, IntFlagEnumAPIModel


class Locale(StrEnumAPIModel):
    """An :class:`~enum.Enum` representing which languages a user can pick on Discord."""
    EN_US = "en-US"  #: English (United States)
    EN_GB = "en-GB"  #: English (Great Britain)
    BG = "bg"  #: Bulgarian
    ZH_CN = "zh-CN"  #: Chinese (China)
    ZH_TW = "zh-TW"  #: Chinese (Taiwan)
    HR = "hr"  #: Croatian
    CS = "cs"  #: Czech
    DA = "da"  #: Danish
    NL = "nl"  #: Dutch
    FI = "fi"  #: Finnish
    FR = "fr"  #: French
    DE = "de"  #: German
    EL = "el"  #: Greek
    HI = "hi"  #: Hindi
    HU = "hu"  #: Hungarian
    IT = "it"  #: Italian
    JA = "ja"  #: Japanese
    KO = "ko"  #: Korean
    LT = "lt"  #: Lithuanian
    NO = "no"  #: Norwegian
    PL = "pl"  #: Polish
    PT_BR = "pt-BR"  #: Portuguese (Brazil)
    RO = "ro"  #: Romanian
    RU = "ru"  #: Russian
    ES_ES = "es-ES"  #: Spanish (Spain)
    SV_SE = "sv-SE"  #: Swedish
    TH = "th"  #: Thai
    TR = "tr"  #: Turkish
    UK = "uk"  #: Ukrainian
    VI = "vi"  #: Vietnamese


class UserFlags(IntFlagEnumAPIModel):
    """An :class:`~enum.IntFlag` enum for a user's possible flags (see the possibilities)."""
    NONE = 0
    STAFF = 1 << 0  #: Discord Employee
    PARTNER = 1 << 1  #: Partnered Server Owner
    HYPESQUAD = 1 << 2  #: HypeSquad Events Coordinator
    BUG_HUNTER_LEVEL_1 = 1 << 3  #: Bug Hunter Level 1
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6  #: House Bravery Member
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7  #: House Brilliance Member
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8  #: House Balance Member
    PREMIUM_EARLY_SUPPORTER = 1 << 9  #: Early Nitro Supporter
    TEAM_PSEUDO_USER = 1 << 10  #: User is a team
    BUG_HUNTER_LEVEL_2 = 1 << 14  #: Bug Hunter Level 2
    VERIFIED_BOT = 1 << 16  #: Verified Bot
    VERIFIED_DEVELOPER = 1 << 17  #: Early Verified Bot Developer
    CERTIFIED_MODERATOR = 1 << 18  #: Discord Certified Moderator
    BOT_HTTP_INTERACTIONS = 1 << 19  #: Bot uses only HTTP interactions and is shown in the online member list


class UserPremiumType(IntEnumAPIModel):
    """An :class:`~enum.IntEnum` listing possible states of a user's Nitro subscription."""

    #: The user does not currently have Nitro.
    NONE = 0

    #: The user currently has a Nitro Classic subscription.
    NITRO_CLASSIC = 1

    #: The user currently has a Nitro subscription.
    NITRO = 2


class ChannelType(IntEnumAPIModel):
    """An :class:`~enum.IntEnum` listing possible :class:`~.Channel` types."""

    #: A text channel in a server.
    GUILD_TEXT = 0

    #: A direct message channel between two users.
    DM = 1

    #: A voice channel in a server.
    GUILD_VOICE = 2

    #: A direct message between multiple users.
    GROUP_DM = 3

    #: An organizational category that may contain up to 50 channels.
    GUILD_CATEGORY = 4

    #: A channel that users can follow and crosspost into their own server.
    GUILD_NEWS = 5

    #: A channel in which game developers can sell their game on Discord.
    GUILD_STORE = 6

    #: A temporary sub-channel within a :attr:`GUILD_NEWS` channel.
    GUILD_NEWS_THREAD = 10

    #: A temporary sub-channel within a :attr:`GUILD_TEXT` channel.
    GUILD_PUBLIC_THREAD = 11

    #: A temporary sub-channel within a :attr:`GUILD_TEXT` channel that is only viewable by those invited and those
    #: with the MANAGE_THREADS permission
    GUILD_PRIVATE_THREAD = 12  # TODO: Link to permission overwrite attr

    #: A voice channel for hosting events with an audience.
    GUILD_STAGE_VOICE = 13


class PermissionFlags(IntFlagEnumAPIModel):
    """An :class:`~enum.IntFlag` for permission flags used by Discord, which determine what members can and can't do.

    See Also:
        :class:`~.PermissionOverwrite`
    """

    #: No permission flags set.
    NONE = 0

    #: Allows creation of instant invites
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>`, :attr:`Voice <ChannelType.GUILD_VOICE>` and
    #: :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    CREATE_INSTANT_INVITE = 1 << 0

    #: Allows kicking members
    KICK_MEMBERS = 1 << 1

    #: Allows banning members
    BAN_MEMBERS = 1 << 2

    #: Allows all permissions and bypasses channel permission overwrites
    ADMINISTRATOR = 1 << 3

    #: Allows management and editing of channels
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>`, :attr:`Voice <ChannelType.GUILD_VOICE>` and
    #: :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    MANAGE_CHANNELS = 1 << 4

    #: Allows management and editing of the guild
    MANAGE_GUILD = 1 << 5

    #: Allows for the addition of reactions to messages (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    ADD_REACTIONS = 1 << 6

    #: Allows for viewing of audit logs
    VIEW_AUDIT_LOG = 1 << 7

    #: Allows for using priority speaker in a voice channel
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` Channels)
    PRIORITY_SPEAKER = 1 << 8

    #: Allows the user to go live (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` Channels)
    STREAM = 1 << 9

    #: Allows guild members to view a channel, which includes reading messages in text channels and joining voice
    #: channels
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>`, :attr:`Voice <ChannelType.GUILD_VOICE>` and
    #: :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    VIEW_CHANNEL = 1 << 10

    #: Allows for sending messages in a channel (does not allow sending messages in threads)
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    SEND_MESSAGES = 1 << 11

    #: Allows for sending of /tts messages (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    SEND_TTS_MESSAGES = 1 << 12

    #: Allows for deletion of other users messages (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    MANAGE_MESSAGES = 1 << 13

    #: Links sent by users with this permission will be auto-embedded
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    EMBED_LINKS = 1 << 14

    #: Allows for uploading images and files (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    ATTACH_FILES = 1 << 15

    #: Allows for reading of message history (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    READ_MESSAGE_HISTORY = 1 << 16

    #: Allows for using the @everyone tag to notify all users in a channel, and the @here tag to notify all online
    #: users in a channel
    #  (Available in :attr:`Text <ChannelType.GUILD_TEXT>` channels)
    MENTION_EVERYONE = 1 << 17

    #: Allows the usage of custom emojis from other servers
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    USE_EXTERNAL_EMOJIS = 1 << 18

    #: Allows for viewing guild insights
    VIEW_GUILD_INSIGHTS = 1 << 19

    #: Allows for joining of a voice channel
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` and :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    CONNECT = 1 << 20

    #: Allows for speaking in a voice channel
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` Channels)
    SPEAK = 1 << 21

    #: Allows for muting members in a voice channel
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` and :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    MUTE_MEMBERS = 1 << 22

    #: Allows for deafening of members in a voice channel
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` and :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    DEAFEN_MEMBERS = 1 << 23

    #: Allows for moving of members between voice channels
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` and :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    MOVE_MEMBERS = 1 << 24

    #: Allows for using voice-activity-detection in a voice channel
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` Channels)
    USE_VAD = 1 << 25

    #: Allows for modification of own nickname
    CHANGE_NICKNAME = 1 << 26

    #: Allows for modification of other users nicknames
    MANAGE_NICKNAMES = 1 << 27

    #: Allows management and editing of roles
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>`, :attr:`Voice <ChannelType.GUILD_VOICE>` and
    #: :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    MANAGE_ROLES = 1 << 28

    #: Allows management and editing of webhooks
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    MANAGE_WEBHOOKS = 1 << 29

    #: Allows management and editing of emojis and stickers
    MANAGE_EMOJIS_AND_STICKERS = 1 << 30

    #: Allows members to use application commands, including slash commands and context menu commands.
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    USE_APPLICATION_COMMANDS = 1 << 31

    #: Allows for requesting to speak in stage channels. (This permission is under active development and may be
    #: changed or removed.)
    #: (Available in :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    REQUEST_TO_SPEAK = 1 << 32

    #: Allows for creating, editing, and deleting scheduled events
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>`, :attr:`Stage <ChannelType.GUILD_STAGE_VOICE>` Channels)
    MANAGE_EVENTS = 1 << 33

    #: Allows for deleting and archiving threads, and viewing all private threads
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    MANAGE_THREADS = 1 << 34

    #: Allows for creating public and announcement threads
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    CREATE_PUBLIC_THREADS = 1 << 35

    #: Allows for creating private threads (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    CREATE_PRIVATE_THREADS = 1 << 36

    #: Allows the usage of custom stickers from other servers
    #: (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    USE_EXTERNAL_STICKERS = 1 << 37

    #: Allows for sending messages in threads (Available in :attr:`Text <ChannelType.GUILD_TEXT>` Channels)
    SEND_MESSAGES_IN_THREADS = 1 << 38

    #: Allows for launching activities (applications with the EMBEDDED flag) in a voice channel
    #: (Available in :attr:`Voice <ChannelType.GUILD_VOICE>` Channels)
    START_EMBEDDED_ACTIVITIES = 1 << 39

    #: Allows for timing out users to prevent them from sending or reacting to messages in chat and threads,
    #: and from speaking in voice and stage channels
    MODERATE_MEMBERS = 1 << 40


class PermissionOverwriteType(IntEnumAPIModel):
    """An :class:`~enum.IntEnum` indicating whether a permission overwrite is targetted towards a user (member) or
    a role."""

    ROLE = 0  #: Indicates the permission overwrite in question is targeted towards all users with a certain role.
    MEMBER = 1  #: Indicates the permission overwrite in question is targeted towards a specific user in a server.

