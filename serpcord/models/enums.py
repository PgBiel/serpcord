from enum import Flag, Enum

from .apimodel import StrEnumAPIModel, IntEnumAPIModel, FlagEnumAPIModel, IntFlagEnumAPIModel


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
