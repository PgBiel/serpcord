from .enums import ChannelType
from .snowflake import Snowflake
from .model_abc import JsonAPIModel
from typing import Mapping, Any, Optional


# class Channel(JsonAPIModel[Mapping[str, Any]]):
#     def __init__(
#         self, channelid: Snowflake, channel_type: ChannelType,
#         *, guild_id: Optional[Snowflake] = None, position: int = 0,
#
#     ):
