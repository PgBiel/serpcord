import typing
import aiohttp
from serpcord.rest.enums import HTTPMethod

API_VERSION = 9
BASE_API_URL = "https://discord.com/api/v9"


class Endpoint:
    """Represents a specific endpoint in the Discord API.

    Attributes:
        method (:class:`~.HTTPMethod`): HTTP Method that this endpoint accepts (GET, POST, PUT, PATCH, or DELETE)
        parts (List[:class:`str`]): Each part (separated /) that composes the endpoint URL (after the base API URL).

    .. testsetup:: *

        from serpcord.rest.enums import HTTPMethod
        from serpcord.rest.endpoint.endpoint import Endpoint
    """

    API_VERSION = API_VERSION
    """Discord API version being currently used in the library."""

    BASE_API_URL = BASE_API_URL
    """Base URL for all API requests."""

    def __init__(self, method: HTTPMethod, parts: typing.Optional[typing.Iterable[str]] = None):
        self.method = method
        self.parts: typing.List[str] = list(parts) or []

    def append_part(self, part: str):
        self.parts.append(part)

    @property
    def url(self) -> str:
        """Returns the full URL by joining (with /) all given parts of this endpoint, and appending them to the
        base API URL.

        Examples
            .. doctest::

                >>> my_endpoint = Endpoint(HTTPMethod.POST, ("users", "@me", "channels"))
                >>> my_endpoint.url
                'https://discord.com/api/v9/users/@me/channels'
        """
        return BASE_API_URL + "/" + ("/".join(self.parts))

    def __repr__(self):
        return f"Endpoint(method={repr(self.method)}, parts={repr(self.parts)})"
