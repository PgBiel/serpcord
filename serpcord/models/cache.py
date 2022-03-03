import typing
import collections.abc

from .model_abc import HasId
from .snowflake import Snowflake
from serpcord.utils.typeutils import SERPCORD_DEFAULT, OrDefault
from typing import Optional, Mapping, Generic, MutableMapping, Dict, Iterable, Union


T = typing.TypeVar("T", bound=HasId)
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
        return self._inner_dict[Snowflake(item)]

    def __delitem__(self, key: Union[int, Snowflake]):
        del self._inner_dict[Snowflake(key)]

    def __setitem__(self, key: Union[int, Snowflake], value: T):
        skey = Snowflake(key)
        if value.id == skey:
            self._inner_dict[skey] = value
        else:
            raise ValueError("Specified value's id does not match the key.")

    def __iter__(self):
        return self._inner_dict.__iter__()

    # def __contains__(self, key: Union[int, Snowflake]):
    #     return key in self._inner_dict

    def add(self, value: T):
        """Adds the given value to the cache, indexing it by ``value.id`` .

        Args:
            value (``T``): The value to append.
        """
        self._inner_dict[value.id] = value

    # def pop(self, value: T):
    #     """Removes the given value from the cache.
    #
    #     Args:
    #         value (``T``): Value to be removed.
    #     """
    #     val_id = Snowflake(value.id)
    #     if val_id in self:
    #         del self[val_id]
