import typing
from .model_abc import JsonAPIModel, Updatable
from .snowflake import Snowflake
from .enums import PermissionFlags, PermissionOverwriteType
from serpcord.utils.model import init_model_from_mapping_json_data
from typing import Mapping, Any, Optional


if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient


class PermissionOverwrite(JsonAPIModel[Mapping[str, Any]]):
    """Represents a Permission Overwrite for a member or role in a channel, allowing or denying a permission
    for the target (either a user - if the target is a user - or all users with a certain role - if the target
    is a role).

    Attributes:
        target_id (:class:`~.Snowflake`): ID of the target of this Permission Overwrite (user or role).
        overwrite_type (:class:`~.PermissionOverwriteType`): The type of the target of this Permission Overwrite
            (:attr:`~.PermissionOverwriteType.USER` or :attr:`~.PermissionOverwriteType.ROLE`).
        allow (:class:`~.PermissionFlags`): The permissions that this overwrite grants to the target in the channel
            the overwrite was created in.
        deny (:class:`~.PermissionFlags`): The permissions that this overwrite revokes from the target in the channel
            the overwrite was created in.
    """
    __slots__ = ("target_id", "overwrite_type", "allow", "deny")

    def __init__(
        self, target_id: Snowflake, overwrite_type: PermissionOverwriteType,
        *, allow: PermissionFlags = PermissionFlags.NONE, deny: PermissionFlags = PermissionFlags.NONE
    ):
        self.target_id: Snowflake = Snowflake(target_id)
        self.overwrite_type: PermissionOverwriteType = PermissionOverwriteType(overwrite_type)
        self.allow: PermissionFlags = PermissionFlags(allow)
        self.deny: PermissionFlags = PermissionFlags(deny)

    @classmethod
    def from_json_data(cls, client, json_data: Mapping[str, Any]):
        return init_model_from_mapping_json_data(
            cls, client, json_data, rename=dict(id="target_id", type="overwrite_type"),
            type_check_types=True
        )

    def __repr__(self):
        return f"{self.__class__.__qualname__}(target_id={self.target_id!r}, overwrite_type={self.overwrite_type!r}, \
allow={self.allow!r}, deny={self.deny!r})"


class RoleTags(JsonAPIModel[Mapping[str, Any]]):
    """Represents a list of flags that describe a :class:`Role`.

    Attributes:
        bot_id (Optional[:class:`~.Snowflake`]): The ID of the bot this role belongs to, if it is a managed role.
        integration_id (Optional[:class:`~.Snowflake`]): The ID of the integration this role belongs to, if it is a
            managed role.
        is_premium_subscriber (:class:`bool`): ``True`` if this is the server's premium subscriber role (given upon
            member boost). ``False`` otherwise (or if unspecified).
    """
    __slots__ = ("bot_id", "integration_id", "is_premium_subscriber")

    def __init__(
        self, *,
        bot_id: Optional[Snowflake] = None, integration_id: Optional[Snowflake] = None,
        is_premium_subscriber: bool = False
    ):
        self.bot_id: Optional[Snowflake] = Snowflake(bot_id) if bot_id is not None else None
        self.integration_id: Optional[Snowflake] = Snowflake(integration_id) if integration_id is not None else None
        self.is_premium_subscriber: bool = bool(is_premium_subscriber)

    @classmethod
    def from_json_data(cls, client, json_data):
        return init_model_from_mapping_json_data(
            cls, client, json_data, rename=dict(premium_subscriber="is_premium_subscriber"),
            type_check_types=False
        )


class Role(JsonAPIModel[Mapping[str, Any]], Updatable):
    """Represents a named set of permissions assigned to groups of members.

    Attributes:
        client (:class:`~.BotClient`): The bot's active client instance.
        guild (Optional[:class:`~.Guild`]): The guild where this role was created (if available).
        id (:class:`~.Snowflake`): The role's ID.
        name (:class:`str`): The role's name.
        color_int (:class:`int`): The role's color, as an integer form of the hexadecimal color.

            .. note::

                If a role assigns no color (``color_int == 0``) to its members, then it doesn't affect its members'
                display color (which is equivalent to the color of the highest role they have with ``color_int != 0``).

        is_hoisted (:class:`bool`): ``True`` if the role appears separately in the member sidebar (all members with this
            role as their highest hoisted role appear separately in the sidebar); ``False`` otherwise (if the role
            doesn't affect the member sidebar organization at all).
        icon_hash (Optional[:class:`str`]): The role's icon hash, if any, or ``None``.
        unicode_emoji (Optional[:class:`str`]): The role's unicode emoji icon, if any, or ``None``.
        position (:class:`int`): The role's position, the lowest being ``0`` (the position of the ``@everyone`` role,
            which is the default role that all members in all guilds have).
        permissions (:class:`~.PermissionFlags`): The permissions granted by this role.

            .. note::

                Members' permissions may vary per channel, depending on :class:`PermissionOverwrite` s in that channel.
                However, if ``PermissionFlags.ADMINISTRATOR in role.permissions`` holds, then members of `role` have
                access to all permissions in every channel, unconditionally.

        is_managed (:class:`bool`): ``True`` if this role belongs to a bot or interaction and cannot be manually deleted
            (without removing the bot or interaction from the server); ``False`` otherwise (was created by a user, and
            may be deleted at will by members with enough permissions).
        is_mentionable (:class:`bool`): ``True`` if all members can ping this role (i.e., issue a notification to all
            members of this role at once), regardless of individual permissions; ``False`` if pinging this role is
            restricted to members with the :attr:`~.PermissionFlags.MENTION_EVERYONE` permission.
        tags (Optional[:class:`RoleTags`]): Special tags regarding this role (refer to :class:`RoleTags` for further
            info), if any are present; ``None`` otherwise (default).
    """
    __slots__ = (
        "client", "id", "name", "color_int", "is_hoisted", "icon_hash", "unicode_emoji", "position", "permissions",
        "is_managed", "is_mentionable", "tags", "guild"
    )

    def __init__(
        self, client: "BotClient", roleid: Snowflake,
        *, name: str, color_int: int, is_hoisted: bool, icon_hash: Optional[str] = None,
        unicode_emoji: Optional[str] = None, position: int, permissions: PermissionFlags, is_managed: bool,
        is_mentionable: bool, tags: Optional[RoleTags] = None
    ):
        self.client = client
        self.id: Snowflake = Snowflake(roleid)
        self.name: str = str(name)
        self.color_int: int = int(color_int)
        self.is_hoisted: bool = bool(is_hoisted)
        self.icon_hash: Optional[str] = str(icon_hash) if icon_hash is not None else None
        self.unicode_emoji: Optional[str] = str(unicode_emoji) if unicode_emoji is not None else None
        self.position: int = int(position)
        self.permissions: PermissionFlags = PermissionFlags(permissions)
        self.is_managed: bool = bool(is_managed)
        self.is_mentionable: bool = bool(is_mentionable)
        self.tags: Optional[RoleTags] = tags

        self.guild = None  # TODO

    @classmethod
    def from_json_data(cls, client: "BotClient", json_data: Mapping[str, Any]) -> "Role":
        """Converts JSON data received from the API into a valid :class:`Role` instance. For internal use only.

        See Also:
            :meth:`JsonAPIModel.from_json_data`
        """
        return init_model_from_mapping_json_data(
            cls, client, json_data,
            rename=dict(
                id="roleid", color="color_int", hoist="is_hoisted", icon="icon_hash",
                managed="is_managed", mentionable="is_mentionable"
            ),
            type_check_types=True
        )

    def __repr__(self):
        return f"<{self.__class__.__qualname__} id={self.id!r}, name={self.name!r}, is_hoisted={self.is_hoisted!r}, \
is_managed={self.is_managed!r}>"
