import abc
import typing
import json
from enum import Enum, EnumMeta, Flag

from serpcord.exceptions.dataparseexc import APIJsonParsedTypeMismatchException, APIDataParseException

TSelfAPIModel = typing.TypeVar("TSelfAPIModel", bound="APIModel")
"""Type var denoting the return of `self` in :class:`APIModel` methods, or of an instance of the own subclass
in class methods.
For example, :meth:`APIModel.from_raw_data`, a classmethod, returns an instance of the APIModel subclass
on which it was called."""

TSelfJsonAPIModel = typing.TypeVar("TSelfJsonAPIModel", bound="JsonAPIModel")
"""Type var denoting the return of `self` in :class:`JsonAPIModel` methods, or of an instance of the own subclass
in class methods.
For example, :meth:`JsonAPIModel.from_json_data`, a classmethod, returns an instance of the JsonAPIModel subclass
on which it was called."""

TParsedJsonType = typing.TypeVar("TParsedJsonType")
"""Type var denoting the type of JSON object a :class:`JsonAPIModel` subclass requires to be constructed.
In other words, if we received a JSON type other than that subclass' ``TParsedJsonType``, then it will
likely raise an error."""

class ABCEnumMeta(abc.ABCMeta, EnumMeta):
    pass

class APIModel(abc.ABC):
    """Abstract class for API Models."""

    @classmethod
    @abc.abstractmethod
    def from_raw_data(cls: typing.Type[TSelfAPIModel], raw_data: str) -> TSelfAPIModel:
        """Abstract method to convert raw string data received from the Discord API to an instance of this model.

        Args:
            raw_data (:class:`str`): The raw string of data received from the Discord API to convert to this model.

        Returns:
            :obj:`~.TSelfAPIModel`: The generated instance of this :class:`APIModel` subclass.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed."""
        raise NotImplementedError


class JsonAPIModel(APIModel, abc.ABC, typing.Generic[TParsedJsonType]):
    """Abstract class for API Models that specifically require JSON parsing.

    Requires one Generic parameter, :obj:`TParsedJsonType` - please refer to its documentation."""

    @classmethod
    def from_raw_data(cls: typing.Type[TSelfJsonAPIModel], raw_data: str) -> TSelfJsonAPIModel:
        """Method to convert raw string data received from the Discord API to an instance of this model.

        The default behavior for :class:`JsonAPIModel` subclasses is simply to parse JSON from the raw string
        (assuming JSON is expected), and then use the abstract (subclass-dependent) :meth:`~.from_json_data`
        method to convert the parsed JSON to an instance.

        Args:
            raw_data (:class:`str`): The raw string of data received from the Discord API to convert to this model.

        Returns:
            :obj:`TSelfJsonAPIModel`: The generated instance of this JsonAPIModel subclass.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        try:
            return cls.from_json_data(json.loads(raw_data))
        except json.JSONDecodeError as e:
            raise APIDataParseException("Malformed JSON data received.") from e

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
            :exc:`APIJsonParsedTypeMismatchException`: If the JSON type received was invalid.
                (Note that this subclasses :class:`TypeError`.)
        """
        raise NotImplementedError


class StrEnumAPIModel(JsonAPIModel[str], Enum, metaclass=ABCEnumMeta):
    @classmethod
    def from_json_data(cls, json_data: str):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


class IntEnumAPIModel(JsonAPIModel[int], Enum, metaclass=ABCEnumMeta):
    @classmethod
    def from_json_data(cls, json_data: int):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e


class FlagEnumAPIModel(JsonAPIModel[int], Flag, metaclass=ABCEnumMeta):
    @classmethod
    def from_json_data(cls, json_data: int):
        try:
            return cls(json_data)
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Invalid Enum value received.") from e
