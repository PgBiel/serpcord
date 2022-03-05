import typing
import collections.abc

from .model_abc import HasId
from .snowflake import Snowflake
from serpcord.utils.typeutils import SERPCORD_DEFAULT, OrDefault
from typing import Optional, Mapping, Generic, MutableMapping, Dict, Iterable, Union, Any


T = typing.TypeVar("T", bound=HasId)
D = typing.TypeVar("D")
if typing.TYPE_CHECKING:
    MutableMappingSnowflakeT = MutableMapping[Snowflake, T]
else:
    MutableMappingSnowflakeT = collections.abc.MutableMapping


class SnowflakeCache(MutableMappingSnowflakeT, Generic[T]):
    """A :class:`~collections.abc.MutableMapping` that serves as a cache for objects (of type ``T``)
    uniquely identified by a Snowflake id."""
    def __init__(self, *objs: T):
        self._inner_dict: Dict[Snowflake, T] = {
            Snowflake(obj.id): obj for obj in objs
        }

    def __len__(self):
        return len(self._inner_dict)

    def __getitem__(self, item: Union[int, Snowflake]) -> T:
        try:
            return self._inner_dict[Snowflake(item)]
        except (TypeError, ValueError):
            return self._inner_dict[item]  # so it remains a KeyError

    def __delitem__(self, key: Union[int, Snowflake]):
        del self._inner_dict[Snowflake(key)]

    def __setitem__(self, key: Union[int, Snowflake], value: T):
        skey = Snowflake(key)
        if value.id == skey:
            self._inner_dict[skey] = value
        else:
            raise ValueError("Specified value's id does not match the given key.")

    def __iter__(self):
        return self._inner_dict.__iter__()

    def __contains__(self, key):
        try:
            return Snowflake(key) in self._inner_dict
        except (TypeError, ValueError):
            return key in self._inner_dict  # keep returning bool

    def add(self, value: T):
        """Adds the given value to the cache, indexing it by ``value.id`` .

        Args:
            value (``T``): The value to append.
        """
        self._inner_dict[value.id] = value

    def remove(self, value: T):
        """Removes the given value from the cache.

        Args:
            value (``T``): The value to be removed.

        Raises:
            :exc:`LookupError`: If there was no such value in the cache.
        """
        for k, v in self.items():
            if v == value:
                del self[k]
        raise LookupError("Value not found in the cache.")
