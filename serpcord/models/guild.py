import typing
import datetime

from typing import Mapping, Any, Optional, Iterable, List
from .model_abc import JsonAPIModel
from .snowflake import Snowflake
from .user import User
from .enums import PermissionFlags
from .permissions import Role
from serpcord.utils.model import _init_model_from_mapping_json_data

if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient


class GuildMember(JsonAPIModel[Mapping[str, Any]]):  # TODO: Optional[Guild] - make sure the guild itself adds itself
    def __init__(self, client: "BotClient", user: User,  # TODO: docs + slots
                 *, nick: Optional[str] = None, guild_avatar_hash: Optional[str] = None,
                 role_ids: Iterable[Snowflake], roles: Iterable[Role], joined_at: datetime.datetime,
                 premium_since: Optional[datetime.datetime] = None,
                 is_deaf: bool, is_muted: bool, is_pending: bool = False,
                 permissions: Optional[PermissionFlags] = None,
                 communication_disabled_until: Optional[datetime.datetime] = None):
        self.client: "BotClient" = client
        self.user: User = user  # NOTE: Must be injected in MESSAGE_CREATE / MESSAGE_UPDATE events (not provided by API)
        self.nick: Optional[str] = str(nick) if nick is not None else None
        self.guild_avatar_hash: Optional[str] = str(guild_avatar_hash) if guild_avatar_hash is not None else None
        self.role_ids: List[Snowflake] = list(role_ids)
        self.joined_at: datetime.datetime = joined_at
        self.premium_since: Optional[datetime.datetime] = premium_since
        self.is_deaf = bool(is_deaf)
        self.is_muted = bool(is_muted)
        self.is_pending = bool(is_pending)
        self.permissions = PermissionFlags(permissions) if permissions is not None else None
        self.communication_disabled_until: Optional[datetime.datetime] = communication_disabled_until

    @property
    def id(self) -> Snowflake:
        return self.user.id

    @property
    def username(self) -> str:
        return self.user.username

    @property
    def display_name(self) -> str:
        return self.nick or self.username

    @classmethod
    def _from_json_data(cls, client: "BotClient", json_data: Mapping[str, Any]):
        return _init_model_from_mapping_json_data(cls, client, json_data, rename=dict(
            avatar="guild_avatar_hash", roles="role_ids", deaf="is_deaf", muted="is_muted", pending="is_pending"
        ), type_check_types=True)
