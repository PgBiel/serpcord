from .serpcordexc import APIRequestException


class APIDataParseException(APIRequestException):
    """Indicates certain data received from Discord could not be correctly parsed, due to being corrupt, invalid,
    or unexpected (say, due to a sudden API version change)."""
    pass


class APIJsonParseException(APIDataParseException):
    """Indicates JSON data from Discord could not be correctly parsed, due to being corrupt, invalid,
    or unexpected (say, due to a sudden API version change)."""
    pass


class APIJsonParsedTypeMismatchException(APIJsonParseException):
    """Indicates that JSON data received through the Discord API did not correspond to the JSON type
    expected by the library. For example, a JSON-based model such as :class:`~.Snowflake` expected an :class:`int`, but
    received a :class:`dict`."""
    pass
