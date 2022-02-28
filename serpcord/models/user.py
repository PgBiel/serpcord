import typing
from typing import Optional, Dict, Type, Mapping, Any

from .apimodel import JsonAPIModel
from .enums import Locale, UserFlags, UserPremiumType
from ..rest.cdn import BASE_CDN_URL
from ..rest.enums import CDNImageFormats
from .snowflake import Snowflake
from ..exceptions.dataparseexc import APIJsonParsedTypeMismatchException


class User(JsonAPIModel[Mapping[str, Any]]):
    """Represents a Discord User.

    Attributes:
        id (:class:`~.Snowflake`): The user's ID.
        username (:class:`str`): The user's username (non-unique).
        discriminator (:class:`str`): The user's four-digit tag (E.g. '1234' in 'username#1234').
        avatar_hash (Optional[:class:`str`]): The user's avatar hash (see :meth:`User.avatar_url`), if any. ``None`` if
            using the default Discord avatar.
        is_bot (:class:`bool`): ``True`` if the user is a bot/OAuth2 app recognized by Discord; ``False`` otherwise
            (regular user).
        is_system (:class:`bool`): ``True`` if the user is an Official Discord System user (which sends official
            urgent warnings and messages); ``False`` otherwise.
        is_mfa_enabled (:class:`bool`): ``True`` if the user has 2FA enabled on their account; ``False`` otherwise.

            .. warning::

                This attribute isn't normally accessible to bots (and defaults to ``False``).

        banner_hash (Optional[:class:`str`]): The user's banner hash, if they are using a banner. ``None`` otherwise.

            .. warning::

                This attribute isn't normally accessible to bots (and defaults to ``None``).

        accent_color_dec (Optional[:class:`int`]): The user's banner color, as a decimal representation of a hex color.
            ``None`` if they are not using a banner.

            .. warning::

                This attribute isn't normally accessible to bots (and defaults to 0).

        locale (:class:`~.Locale`): The user's chosen language option, if available. Defaults to :attr:`~.Locale.EN_US`.

            .. warning::

                This attribute isn't normally accessible to bots (and defaults to :attr:`Locale.EN_US <.Locale.EN_US>`).

        is_verified (:class:`bool`): ``True`` if this user's email was verified; ``False`` otherwise.

            .. warning::

                This attribute isn't normally accessible to bots (and defaults to ``False``).

        email (Optional[:class:`str`]): The user's email, if available. ``None`` otherwise.

            .. warning::

                This attribute isn't normally accessible to bots (and defaults to ``None``).

        flags (:class:`~.UserFlags`): The User's flags. (Refer to :class:`~.UserFlags` for a list.)
        premium_type (:class:`~.UserPremiumType`): The type of Nitro subscription the User has. (Refer to
            :class:`~.UserPremiumType` for a list.)

            .. warning::

                This attribute isn't normally accessible to bots (and defaults to
                :attr:`UserPremiumType.NONE <.UserPremiumType.NONE>`).

        public_flags (:class:`~.UserFlags`): The User's public flags. (Refer to :class:`~.UserFlags` for a list.)
    """

    def __init__(
            self, userid: Snowflake,
            *, username: str, discriminator: str,
            avatar_hash: Optional[str] = None, is_bot: bool = False, is_system: bool = False,
            is_mfa_enabled: bool = False,
            banner_hash: Optional[str] = None, accent_color_dec: Optional[int] = None,
            locale: Locale = Locale.EN_US, is_verified: bool = False, email: Optional[str] = None,
            flags: UserFlags = UserFlags.NONE, premium_type: UserPremiumType = UserPremiumType.NONE,
            public_flags: UserFlags = UserFlags.NONE
    ):
        self.id: Snowflake = userid
        self.username: str = username
        self.discriminator: str = discriminator
        self.avatar_hash: Optional[str] = avatar_hash
        self.is_bot: bool = is_bot
        self.is_system: bool = is_system
        self.is_mfa_enabled: bool = is_mfa_enabled
        self.banner_hash: Optional[str] = banner_hash
        self.accent_color_dec: Optional[int] = accent_color_dec
        self.locale: Locale = locale
        self.is_verified: bool = is_verified
        self.email: Optional[str] = email
        self.flags: UserFlags = flags
        self.premium_type: UserPremiumType = premium_type
        self.public_flags: UserFlags = public_flags

    @classmethod
    def from_json_data(cls, json_data: Mapping[str, Any]):
        """Constructs a :class:`User` from received JSON data.

        Args:
            json_data (Mapping[:class:`str`, Any]): The data to parse and construct a User instance with.
                (Usually a :class:`dict`.)

        Raises:
            :exc:`APIJsonParsedTypeMismatchException`: If the given data wasn't valid user data.
        """
        expected_keys = [
            "id", "username", "discriminator", "avatar", "bot", "system", "mfa_enabled", "banner", "accent", "color",
            "locale", "verified", "email", "flags", "premium_type", "public", "flags"
        ]
        key_map = {
            "id": "userid", "avatar": "avatar_hash", "bot": "is_bot", "system": "is_system",
            "mfa_enabled": "is_mfa_enabled", "banner": "banner_hash", "accent_color": "accent_color_dec",
            "verified": "is_verified"
        }
        val_model_map = {
            "id": Snowflake,
            "locale": Locale,
            "flags": UserFlags,
            "premium_type": UserPremiumType,
            "public_flags": UserFlags
        }
        try:
            return cls(**dict(
                (
                    key_map.get(k, k),
                    typing.cast(Type[JsonAPIModel], val_model_map.get(v)).from_json_data(v)
                    if (v_ := val_model_map.get(v)) and issubclass(v_, JsonAPIModel) else v
                )
                for k, v in json_data.items() if k in expected_keys
            ))
        except (AttributeError, TypeError, ValueError) as e:
            raise APIJsonParsedTypeMismatchException("Unexpected User JSON data received.") from e

    def avatar_url(self, img_format: CDNImageFormats = CDNImageFormats.PNG) -> str:
        """Returns this user's avatar URL, in the given format (or PNG by default).

        Args:
            img_format (:class:`~.CDNImageFormats`, optional): The image format of the image in the resulting URL.
                Defaults to :class:`CDNImageFormats.PNG <.CDNImageFormats.PNG>`.

        Returns:
            :class:`str`: The generated avatar URL, with the specified image format.

        Examples:
            .. testsetup:: avatar_url

                from serpcord.models.snowflake import Snowflake
                from serpcord.models.user import User
                from serpcord.rest.enums import CDNImageFormats
                user = User(Snowflake(12345), username="xxx", discriminator="1234", avatar_hash="abcabcabc")
            .. doctest:: avatar_url

                >>> user.id.value
                12345
                >>> user.avatar_hash
                'abcabcabc'
                >>> user.avatar_url()
                'https://cdn.discordapp.com/avatars/12345/abcabcabc.png'
                >>> user.avatar_url(CDNImageFormats.JPEG)
                'https://cdn.discordapp.com/avatars/12345/abcabcabc.jpeg'
                >>> user.avatar_url(CDNImageFormats.GIF)
                'https://cdn.discordapp.com/avatars/12345/a_abcabcabc.gif'
        """
        file_ext: str = CDNImageFormats(img_format).file_extension
        u_id: str = str(self.id.value)
        u_avh: str = str(self.avatar_hash)
        return f"{BASE_CDN_URL}avatars/{u_id}/{'a_' if img_format == CDNImageFormats.GIF else ''}{u_avh}{file_ext}"
