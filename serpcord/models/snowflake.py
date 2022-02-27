import datetime
from .apimodel import JsonAPIModel
from ..exceptions.dataparseexc import APIJsonParsedTypeMismatchException, APIDataParseException


class Snowflake(JsonAPIModel[int]):
    """Represents Discord's Snowflakes, or unique numeric IDs which are generated based on when the object
    with that ID was created in respect to Discord's epoch (first second of 2015, as per the API Docs).
    Thus, it is possible to retrieve when any object uniquely identified by a Snowflake (which includes most common
    ones - guilds/servers, users, roles, channels, and so on) was created.

    Note:
        Use :attr:`Snowflake.DISCORD_EPOCH` to refer to Discord's epoch timestamp (in seconds) as an int.

    Attributes:
        value (:class:`int`): Raw value of this Snowflake, which contains the encoded timestamp of when this object was
            created.

    .. testsetup:: *

        import datetime
        from serpcord.models import Snowflake
        sample_snowflake = Snowflake(value=613425648685547541)
    """

    DISCORD_EPOCH: int = 1420070400  # timestamp in seconds (first second of 2015)
    """Discord's epoch Unix timestamp (in seconds), equivalent to the first second of 2015."""

    def __init__(self, value: int):
        self.value: int = value

    @classmethod
    def from_raw_data(cls, raw_data: str):
        """Generates a Snowflake from raw Discord data, by instantiating with ``Snowflake(int(raw_data))``.

        Args:
            raw_data (:class:`str`): Raw data from Discord to be parsed into a Snowflake instance.

        Returns:
            :class:`Snowflake`: The Snowflake instance generated from the given data.

        Raises:
            :exc:`APIDataParseException`: If the given data can't be directly coverted to an :class:`int`.
        """
        super().from_raw_data(raw_data)

    @classmethod
    def from_json_data(cls, json_data: int):
        """Generates a Snowflake from parsed JSON data (int), by instantiating with ``Snowflake(int(raw_data))``.

        Args:
            json_data (:class:`int`): JSON data from Discord to be parsed into a Snowflake instance.

        Returns:
            :class:`Snowflake`: The Snowflake instance generated from the given data.

        Raises:
            :exc:`APIJsonParsedTypeMismatchException`: If the given JSON data isn't an :class:`int`.
        """
        try:
            return cls(int(json_data))
        except ValueError as e:
            raise APIJsonParsedTypeMismatchException("Snowflake data must be an int (its value).") from e

    @property
    def timestamp(self) -> int:
        """Retrieves the Unix timestamp (in seconds) of when the object represented by this Snowflake was created.

        Examples:
            .. doctest::

                >>> sample_snowflake  # sample snowflake using Discord Developers server ID
                Snowflake(value=613425648685547541)
                >>> sample_snowflake.timestamp  # timestamp of when the object identified by this Snowflake was created
                1566322471
        """
        return ((self.value >> 22) // 1000) + Snowflake.DISCORD_EPOCH

    @property
    def datetime(self) -> datetime.datetime:
        """Retrieves the :class:`~datetime.datetime` object of when the object represented by this snowflake was
        created.

        Note:
            The datetime object is returned in local time, as a naive object (without timezone reference).
            Use :meth:`Snowflake.utcdatetime` for an aware (with timezone reference) UTC datetime.

        Examples:
            .. doctest::

                >>> sample_snowflake  # sample snowflake using Discord Developers server ID
                Snowflake(value=613425648685547541)
                >>> dt = sample_snowflake.datetime  # datetime of when the object identified by that ID was created
                >>> dt.astimezone(datetime.timezone.utc)  # converts the above datetime (in local time) to UTC
                datetime.datetime(2019, 8, 20, 17, 34, 31, tzinfo=datetime.timezone.utc)
        """
        return datetime.datetime.fromtimestamp(self.timestamp)

    @property
    def utcdatetime(self) -> "datetime.datetime":
        """Retrieves the UTC :class:`~datetime.datetime` object of when the object represented by this snowflake was
        created.

        Note:
            The datetime object is returned in UTC, as an aware (with +0 timezone reference) object.
            Use :meth:`Snowflake.datetime` for a naive (without timezone reference) datetime using
            local (system) time.

        Examples:
            .. doctest::

                >>> sample_snowflake  # sample snowflake using Discord Developers server ID
                Snowflake(value=613425648685547541)
                >>> sample_snowflake.utcdatetime  # UTC datetime of when the object identified by that ID was created
                datetime.datetime(2019, 8, 20, 17, 34, 31, tzinfo=datetime.timezone.utc)
        """
        return datetime.datetime.fromtimestamp(self.timestamp, tz=datetime.timezone.utc)

    @classmethod
    def from_timestamp(cls, timestamp: int):
        """Generates a Snowflake from a given timestamp integer.

        Args:
            timestamp: The timestamp (in seconds) from which a Snowflake should be generated.

        Returns:
            :class:`Snowflake`: A Snowflake `s` such that `s.timestamp` is equal to the given timestamp.

        Examples:
            .. doctest::

                >>> timestamp = 1566322471  # seconds!
                >>> gen_snowflake = Snowflake.from_timestamp(timestamp)
                >>> assert gen_snowflake.timestamp == timestamp
        """
        return Snowflake(value=((timestamp - Snowflake.DISCORD_EPOCH)*1000) << 22)

    @classmethod
    def from_datetime(cls, dt: "datetime.datetime"):
        """Generates a Snowflake from a given :class:`~datetime.datetime` instance.

        Args:
            dt: The :class:`~datetime.datetime` object from which a Snowflake should be generated.

        Returns:
            :class:`Snowflake`: A Snowflake `s` such that `s.datetime` is equal to the given datetime object (if naive).

        Examples:
            .. doctest::

                >>> dt = datetime.datetime(2019, 8, 20, 17, 34, 31)
                >>> gen_snowflake = Snowflake.from_datetime(dt)
                >>> assert gen_snowflake.datetime == dt  # original datetime must be naive (no tz) for this to hold
        """
        return cls.from_timestamp(int(dt.timestamp()))

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"Snowflake(value={repr(self.value)})"

    def __int__(self):
        return self.value
