__all__ = ("User", "BotUser")
import typing
import io
from typing import Optional, Dict, Type, Mapping, Any, Union

from .model_abc import JsonAPIModel, Updatable, HasId
from .enums import Locale, UserFlags, UserPremiumType
from ..rest.cdn import BASE_CDN_URL
from ..rest.enums import CDNImageFormats
from .snowflake import Snowflake
from ..exceptions.dataparseexc import APIJsonParsedTypeMismatchException, APIJsonParseException
from serpcord.rest.endpoint.user import PatchCurrentUserEndpoint
from serpcord.utils.typeutils import SERPCORD_DEFAULT, OrDefault, OptionalOrDefault

if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient


class User(JsonAPIModel[Mapping[str, Any]], Updatable, HasId):
    """Represents a Discord User.

    Attributes:
        client (:class:`~.BotClient`): The bot's active client instance.
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

        accent_color_int (Optional[:class:`int`]): The user's banner color, as an integer representation of a hex color.
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
    __slots__ = (
        "client", "username", "discriminator", "avatar_hash", "is_bot", "is_system", "is_mfa_enabled",
        "banner_hash", "accent_color_int", "locale", "is_verified", "email", "flags", "premium_type", "public_flags"
    )

    def __init__(self, client: "BotClient", userid: Snowflake,
                 *, username: str, discriminator: str,
                 avatar_hash: Optional[str] = None, is_bot: bool = False, is_system: bool = False,
                 is_mfa_enabled: bool = False,
                 banner_hash: Optional[str] = None, accent_color_int: Optional[int] = None,
                 locale: Locale = Locale.EN_US, is_verified: bool = False, email: Optional[str] = None,
                 flags: UserFlags = UserFlags.NONE, premium_type: UserPremiumType = UserPremiumType.NONE,
                 public_flags: UserFlags = UserFlags.NONE):
        self.client: "BotClient" = client
        self.id: Snowflake = Snowflake(userid)
        self.username: str = str(username)
        self.discriminator: str = str(discriminator)
        self.avatar_hash: Optional[str] = str(avatar_hash) if avatar_hash is not None else None
        self.is_bot: bool = bool(is_bot)
        self.is_system: bool = bool(is_system)
        self.is_mfa_enabled: bool = bool(is_mfa_enabled)
        self.banner_hash: Optional[str] = str(banner_hash) if banner_hash is not None else None
        self.accent_color_int: Optional[int] = int(accent_color_int) if accent_color_int is not None else None
        self.locale: Locale = locale
        self.is_verified: bool = bool(is_verified)
        self.email: Optional[str] = str(email) if email is not None else None
        self.flags: UserFlags = UserFlags(flags)
        self.premium_type: UserPremiumType = UserPremiumType(premium_type)
        self.public_flags: UserFlags = UserFlags(public_flags)

    @classmethod
    def _from_json_data(cls, client, json_data: Mapping[str, Any]):
        """Constructs a :class:`User` from received JSON data.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            json_data (Mapping[:class:`str`, Any]): The data to parse and construct a User instance with.
                (Usually a :class:`dict`.)

        Raises:
            :exc:`APIJsonParsedTypeMismatchException`: If the given data wasn't valid user data.
        """
        expected_keys = [
            "id", "username", "discriminator", "avatar", "bot", "system", "mfa_enabled", "banner", "accent_color",
            "locale", "verified", "email", "flags", "premium_type", "public", "flags"
        ]
        key_map = {
            "id": "userid", "avatar": "avatar_hash", "bot": "is_bot", "system": "is_system",
            "mfa_enabled": "is_mfa_enabled", "banner": "banner_hash", "accent_color": "accent_color_int",
            "verified": "is_verified"
        }
        val_model_map = {
            "id": Snowflake,
            "locale": Locale,
            "flags": UserFlags,
            "premium_type": UserPremiumType,
            "public_flags": UserFlags
        }
        data = {
            **json_data,
            "client": client
        }
        try:
            return cls(**dict(
                (
                    key_map.get(k, k),
                    typing.cast(Type[JsonAPIModel], v_)._from_json_data(client, v)
                    if (v_ := val_model_map.get(k)) and issubclass(v_, JsonAPIModel) else v
                )
                for k, v in data.items() if k in expected_keys
            ))
        except (TypeError, ValueError) as e:
            raise APIJsonParsedTypeMismatchException("Unexpected User JSON data received.") from e
        except AttributeError as e:
            raise APIJsonParseException("Unexpected User JSON data received.") from e

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
                from serpcord.botclient import BotClient
                bot = BotClient("123")
                user = User(bot, Snowflake(12345), username="xxx", discriminator="1234", avatar_hash="abcabcabc")
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

    def __repr__(self):
        class_qname = self.__class__.__qualname__
        return f"<{class_qname} id={repr(self.id)}, username={repr(self.username)}, \
discriminator={repr(self.discriminator)}, is_bot={repr(self.is_bot)}, is_system={repr(self.is_system)}>"


class BotUser(User):
    """A special :class:`User` -derived class representing specifically the current active bot's user.
    Besides :class:`User`'s members, it has a few extra methods.
    """
    __slots__ = ()  # same attrs as User's

    async def modify(
        self,
        *, username: OrDefault[str] = SERPCORD_DEFAULT,
        avatar: OptionalOrDefault[Union[bytes, io.IOBase]] = SERPCORD_DEFAULT
    ) -> "BotUser":
        """Modifies the running bot's user. (Has a lengthy ratelimit, so use with caution!)

        Args:
            username (:class:`str`, optional): The bot user's new username. (Don't specify to leave unchanged.)
            avatar (Union[:class:`bytes`, :class:`io.IOBase`], optional): The bot user's new avatar image.
                (Don't specify to leave unchanged; specify ``None`` to remove an existing avatar.)

        Returns:
            :class:`~.BotUser`: The modified bot user.
        """
        endpoint = PatchCurrentUserEndpoint(username=str(username), avatar=avatar)
        new_bot_user = (await self.client.requester.request_endpoint(endpoint)).parsed_response
        if new_bot_user:
            self._update(new_bot_user)
        return self

    async def set_username(self, username: str) -> "BotUser":
        """Modifies the running bot's user. Has a lengthy ratelimit, so use with caution!

        Args:
            username (:class:`str`): The bot user's new username.

        Returns:
            :class:`~.BotUser`: The modified bot user.
        """
        return await self.modify(username=str(username))

    async def set_avatar(self, avatar: Optional[Union[bytes, io.IOBase]]) -> "BotUser":
        """Modifies the running bot's avatar. Has a lengthy ratelimit, so use with caution!

        Args:
            avatar (Optional[Union[:class:`bytes`, :class:`io.IOBase`]]): The bot user's new avatar image.
                (Specify ``None`` to remove an existing avatar.)

        Returns:
            :class:`~.BotUser`: The modified bot user.
        """
        return await self.modify(avatar=avatar)
