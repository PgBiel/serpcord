import abc
import typing

from serpcord.utils.model import _init_model_from_mapping_json_data
from .enums import ChannelType
from .snowflake import Snowflake
from .model_abc import JsonAPIModel, Updatable, HasId
from .permissions import PermissionOverwrite
from typing import Mapping, Any, Optional, List, Iterable


if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient


class Channel(JsonAPIModel[Mapping[str, Any]], Updatable, HasId, abc.ABC):
    """Abstract base class that represents a channel in Discord, or the basic means of communication.
    Can be of multiple types -
    :class:`Text <TextChannel>`, :class:`Voice <VoiceChannel>`, :class:`DM <DMChannel>`, and so on (refer to
    :class:`~.ChannelType` for a full list.)
    You'll generally never work with this class directly, as it is only a base for the more specialized
    channel types.

    Attributes:
        id (:class:`~.Snowflake`): The channel's unique ID.
        channel_type (:class:`~.ChannelType`): The channel's type.
    """
    __slots__ = ("channel_type",)

    def __init__(
        self, channelid: Snowflake, channel_type: ChannelType
    ):
        self.id = Snowflake(channelid)
        self.channel_type = ChannelType(channel_type)

    @classmethod
    @abc.abstractmethod
    def _from_json_data(cls, client: "BotClient", json_data: Mapping[str, Any]):
        """Builds a Channel instance from received API data."""
        pass


class SendingChannel(Channel, abc.ABC):
    """Abstract base class for channels in which :class:`Message` s can be sent.

    Attributes:
        id (:class:`~.Snowflake`): The channel's unique ID.
        channel_type (:class:`~.ChannelType`): The channel's type.
    """
    __slots__ = ()

    def __init__(self, channelid: Snowflake, channel_type: ChannelType):
        super().__init__(channelid, channel_type)

    @classmethod
    @abc.abstractmethod
    def _from_json_data(cls, client: "BotClient", json_data: Mapping[str, Any]):
        """Builds a SendingChannel instance from received API data."""
        pass

# TODO
