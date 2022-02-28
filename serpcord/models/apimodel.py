import abc
import typing
import json
from enum import Enum, EnumMeta, Flag, IntEnum, IntFlag
from typing import TypeVar

import aiohttp

from serpcord.exceptions.dataparseexc import APIJsonParsedTypeMismatchException, APIDataParseException, \
    APIJsonParseException

TSelfAPIModel = TypeVar("TSelfAPIModel", bound="APIModel")
"""Type var denoting the return of `self` in :class:`APIModel` methods, or of an instance of the own subclass
in class methods.
For example, :meth:`APIModel.from_raw_data`, a classmethod, returns an instance of the APIModel subclass
on which it was called."""

TSelfJsonAPIModel = TypeVar("TSelfJsonAPIModel", bound="JsonAPIModel")
"""Type var denoting the return of `self` in :class:`JsonAPIModel` methods, or of an instance of the own subclass
in class methods.
For example, :meth:`JsonAPIModel.from_json_data`, a classmethod, returns an instance of the JsonAPIModel subclass
on which it was called."""

TParsedJsonType = typing.TypeVar("TParsedJsonType")
"""Type var denoting the type of JSON object a :class:`JsonAPIModel` subclass requires to be constructed.
In other words, if we received a JSON type other than that subclass' ``TParsedJsonType``, then it will
likely raise an error."""


class _ABCEnumMeta(EnumMeta, abc.ABCMeta):
    pass


class APIModel(abc.ABC):
    """Abstract class for API Models."""

    @classmethod
    @abc.abstractmethod
    async def from_response(cls: typing.Type[TSelfAPIModel], response: aiohttp.ClientResponse) -> TSelfAPIModel:
        """Abstract method to convert response data received from the Discord API to an instance of this model.

        Args:
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

    @classmethod
    async def from_response(cls: typing.Type[TSelfJsonAPIModel], response: aiohttp.ClientResponse) -> TSelfJsonAPIModel:
        """Method to convert response data received from the Discord API to an instance of this model.

        The default behavior for :class:`JsonAPIModel` subclasses is simply to parse JSON from the response
        (assuming JSON is expected), and then use the abstract (subclass-dependent) :meth:`~.from_json_data`
        method to convert the parsed JSON to an instance.

        Args:
            response (:class:`aiohttp.ClientRespond`): The response data received from the Discord API to convert to
                this model.

        Returns:
            :obj:`TSelfJsonAPIModel`: The generated instance of this JsonAPIModel subclass.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        try:
            return cls.from_json_data(await response.json())
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
            raise APIJsonParseException("Malformed/non-JSON data received.") from e

    @classmethod
    @abc.abstractmethod
    def from_json_data(cls: typing.Type[TSelfJsonAPIModel], json_data: TParsedJsonType) -> TSelfJsonAPIModel:
        """Abstract method to convert parsed JSON data from the Discord API to an instance of this model.

        Args:
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
    def from_json_data(cls, json_data: str):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


class IntEnumAPIModel(JsonAPIModel[int], IntEnum, metaclass=_ABCEnumMeta):
    """Base class for int :class:`~enum.Enum`-based models."""
    @classmethod
    def from_json_data(cls, json_data: int):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


class IntFlagEnumAPIModel(JsonAPIModel[int], IntFlag, metaclass=_ABCEnumMeta):  # type: ignore
    """Base class for :class:`~enum.IntFlag`-based models."""              # (type ignore necessary due to issue below:)
    @classmethod                                                           # https://github.com/python/mypy/issues/9319
    def from_json_data(cls, json_data: int):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


class FlagEnumAPIModel(JsonAPIModel[int], Flag, metaclass=_ABCEnumMeta):
    """Base class for :class:`~enum.Flag`-based models."""
    @classmethod
    def from_json_data(cls, json_data: int):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e
