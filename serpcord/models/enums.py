from enum import Flag, Enum

from .apimodel import StrEnumAPIModel, IntEnumAPIModel, FlagEnumAPIModel


class Locale(StrEnumAPIModel):
    """An :class:`~enum.Enum` representing which languages a user can pick on Discord."""
    EN_US = "en-US"
    EN_GB = "en-GB"
    BG = "bg"
    ZH_CN = "zh-CN"
    ZH_TW = "zh-TW"
    HR = "hr"
    CS = "cs"
    DA = "da"
    NL = "nl"
    FI = "fi"
    FR = "fr"
    DE = "de"
    EL = "el"
    HI = "hi"
    HU = "hu"
    IT = "it"
    JA = "ja"
    KO = "ko"
    LT = "lt"
    NO = "no"
    PL = "pl"
    PT_BR = "pt-BR"
    RO = "ro"
    RU = "ru"
    ES_ES = "es-ES"
    SV_SE = "sv-SE"
    TH = "th"
    TR = "tr"
    UK = "uk"
    VI = "vi"


class UserFlags(FlagEnumAPIModel):
    """A :class:`~enum.Flag` enum for a user's possible flags (see the possibilities)."""
    NONE = 0
    STAFF = 1 << 0
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSEUDO_USER = 1 << 10
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19


class UserPremiumType(IntEnumAPIModel):
    """An :class:`~enum.Enum` listing possible states of a user's Nitro subscription."""

    #: The user does not currently have Nitro.
    NONE = 0

    #: The user currently has a Nitro Classic subscription.
    NITRO_CLASSIC = 1

    #: The user currently has a Nitro subscription.
    NITRO = 2
