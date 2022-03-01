__all__ = ("SERPCORD_DEFAULT", "SerpcordDefaultType", "OrDefault", "OptionalOrDefault")
import typing


class SerpcordDefaultType:
    """Value that indicates that nothing was specified. Used to disambiguate from ``None`` in contexts
    where ``None`` is meaningful. For example, when setting some parameter to ``None`` would delete something, but
    not setting it to anything would keep everything as is. (Occurs often in ``modify`` methods in models.)"""
    pass


SERPCORD_DEFAULT = SerpcordDefaultType()
T = typing.TypeVar("T")
OrDefault = typing.Union[T, SerpcordDefaultType]
OptionalOrDefault = typing.Union[typing.Optional[T], SerpcordDefaultType]
