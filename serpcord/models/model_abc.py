import abc
import typing
import copy
import json
from enum import Enum, EnumMeta, Flag, IntEnum, IntFlag
from typing import TypeVar, Mapping, Any, Optional

import aiohttp

from serpcord.exceptions.dataparseexc import APIJsonParsedTypeMismatchException, APIDataParseException, \
    APIJsonParseException

TSelfAPIModel = TypeVar("TSelfAPIModel", bound="APIModel")
"""Type var denoting `self` in :class:`APIModel` methods, or an instance of the own subclass
in class methods.
For example, :meth:`APIModel.from_raw_data`, a classmethod, returns an instance of the APIModel subclass
on which it was called."""

TSelfJsonAPIModel = TypeVar("TSelfJsonAPIModel", bound="JsonAPIModel")
"""Type var denoting `self` in :class:`JsonAPIModel` methods, or an instance of the own subclass
in class methods.
For example, :meth:`JsonAPIModel.from_json_data`, a classmethod, returns an instance of the JsonAPIModel subclass
on which it was called."""

TParsedJsonType = typing.TypeVar("TParsedJsonType")
"""Type var denoting the type of JSON object a :class:`JsonAPIModel` subclass requires to be constructed.
In other words, if we received a JSON type other than that subclass' ``TParsedJsonType``, then it will
likely raise an error."""


if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient


class _ABCEnumMeta(EnumMeta, abc.ABCMeta):
    pass


class APIModel(abc.ABC):
    """Abstract class for API Models."""
    __slots__ = ()

    @classmethod
    @abc.abstractmethod
    async def from_response(
        cls: typing.Type[TSelfAPIModel], client: "BotClient", response: aiohttp.ClientResponse
    ) -> TSelfAPIModel:
        """Abstract method to convert response data received from the Discord API to an instance of this model.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): The response data received from the Discord API to convert to
                this model.

        Returns:
            :obj:`~.TSelfAPIModel`: The generated instance of this :class:`APIModel` subclass.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed."""
        raise NotImplementedError


class JsonAPIModel(APIModel, abc.ABC, typing.Generic[TParsedJsonType]):
    """Abstract class for API Models that specifically require JSON parsing.

    Requires one Generic parameter, :obj:`TParsedJsonType`, which indicates which JSON data type
    is required to construct this model (e.g. :class:`~.Snowflake` requires an :class:`int`; :class:`~.User` requires a
    :class:`dict`; and so on."""
    __slots__ = ()

    @classmethod
    async def from_response(
        cls: typing.Type[TSelfJsonAPIModel], client: "BotClient", response: aiohttp.ClientResponse
    ) -> TSelfJsonAPIModel:
        """Method to convert response data received from the Discord API to an instance of this model.

        The default behavior for :class:`JsonAPIModel` subclasses is simply to parse JSON from the response
        (assuming JSON is expected), and then use the abstract (subclass-dependent) :meth:`~.from_json_data`
        method to convert the parsed JSON to an instance.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientRespond`): The response data received from the Discord API to convert to
                this model.

        Returns:
            :obj:`TSelfJsonAPIModel`: The generated instance of this JsonAPIModel subclass.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        try:
            return cls.from_json_data(client, await response.json())
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
            raise APIJsonParseException("Malformed/non-JSON data received.") from e

    @classmethod
    @abc.abstractmethod
    def from_json_data(
        cls: typing.Type[TSelfJsonAPIModel], client: "BotClient", json_data: TParsedJsonType
    ) -> TSelfJsonAPIModel:
        """Abstract method to convert parsed JSON data from the Discord API to an instance of this model.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            json_data (:obj:`~.TParsedJsonType`): The parsed JSON data with which this model should be instantiated,
                necessarily in the type required by this :class:`JsonAPIModel` subclass.

        Returns:
            :obj:`~.TSelfJsonAPIModel`: The generated instance of this JsonAPIModel subclass.

        Raises:
            :exc:`APIJsonParseException`: If the JSON received was invalid, or didn't match the expected type.
        """
        raise NotImplementedError


class StrEnumAPIModel(JsonAPIModel[str], Enum, metaclass=_ABCEnumMeta):
    """Base class for string :class:`~enum.Enum`-based models."""

    @classmethod
    def from_json_data(cls, _c, json_data: str):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


class IntEnumAPIModel(JsonAPIModel[int], IntEnum, metaclass=_ABCEnumMeta):
    """Base class for int :class:`~enum.Enum`-based models."""

    @classmethod
    def from_json_data(cls, _c, json_data: int):
        try:
            return cls(int(json_data))
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


class IntFlagEnumAPIModel(JsonAPIModel[int], IntFlag, metaclass=_ABCEnumMeta):  # type: ignore
    """Base class for :class:`~enum.IntFlag`-based models."""              # (type ignore necessary due to issue below:)
                                                                           # https://github.com/python/mypy/issues/9319
    @classmethod
    def from_json_data(cls, _c, json_data: int):
        try:
            return cls(int(json_data))
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


class FlagEnumAPIModel(JsonAPIModel[int], Flag, metaclass=_ABCEnumMeta):
    """Base class for :class:`~enum.Flag`-based models."""

    @classmethod
    def from_json_data(cls, _c, json_data: int):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


TSelf = typing.TypeVar("TSelf", bound="Updatable")


class Updatable:
    """Helper class that allows subclasses' instances to copy other instances' data."""
    __slots__ = ()

    def _update(self: TSelf, other: TSelf, *, deepcopy: bool = False):
        """Update this instance by replacing its data with another instance's (using solely
        ``__dict__`` and ``__slots__``).

        Args:
            other: Other instance from which data should be copied to the current instance.
            deepcopy (:class:`bool`, optional): If ``True``, `other` will be deepcopied before proceeding.

        Examples:
            .. testsetup::

                from serpcord import BotClient, Role, Snowflake, PermissionFlags
                bot = BotClient("123")
                role1 = Role(bot, Snowflake(123), name="Role A", color_dec=0, is_hoisted=False, position=0, \
permissions=PermissionFlags.NONE, is_managed=False, is_mentionable=True)
                role2 = Role(bot, Snowflake(123), name="Role B", color_dec=0x00FF00, is_hoisted=True, position=3, \
permissions=PermissionFlags.MANAGE_ROLES, is_managed=False, is_mentionable=False)
            .. doctest::

                >>> role1
                <Role id=Snowflake(value=123), name='Role A', is_hoisted=False, is_managed=False>
                >>> role2
                <Role id=Snowflake(value=123), name='Role B', is_hoisted=True, is_managed=False>
                >>> role1._update(role2)  # copies role2's references to role1
                >>> role1
                <Role id=Snowflake(value=123), name='Role B', is_hoisted=True, is_managed=False>
        """
        actual_other = copy.deepcopy(other) if deepcopy else other
        dict_from = getattr(self, "__dict__", None)
        dict_to = getattr(actual_other, "__dict__", None)
        if dict_from and dict_to:  # update dicts
            self.__dict__.update(actual_other.__dict__)

        slots_from: typing.List[str] = []  # copying slots, if there are any (they don't show up in __dict__)
        for cls_from in self.__class__.__mro__:
            slots_from += getattr(cls_from, "__slots__", tuple())

        for slot in slots_from:
            if hasattr(self, slot) and hasattr(actual_other, slot):
                setattr(self, slot, getattr(actual_other, slot))
