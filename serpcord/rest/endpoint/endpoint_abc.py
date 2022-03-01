"""Module for base endpoint classes (all abstract).

Hierarchy:
:class:`Endpoint` > (:class:`GETEndpoint`, :class:`POSTEndpoint`,
:class:`PATCHEndpoint`, :class:`PUTEndpoint`, :class:`DELETEEndpoint`)
"""
import typing
import abc
import aiohttp
from typing import Optional, Iterable, Any, List, Dict, TypeVar
from ..enums import HTTPMethod, HTTPDataType
from ..helpers import HTTPSentData, Response

API_VERSION = 9  #: Discord API version being currently used in the library.
BASE_API_URL = f"https://discord.com/api/v{API_VERSION}/"  #: Base URL for all API requests.

GT = TypeVar("GT")
"""Type parameter for parsed received data models for :class:`Endpoint` subclasses. I.e., for any Endpoint subclass,
the method :meth:`Endpoint.parse_response` always converts raw data received from the API
(usually JSON) to an instance of ``GT``, whatever it may be (which depends on the subclass)."""
# TODO: examples (GT, ST)

if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient



class Endpoint(abc.ABC, typing.Generic[GT]):
    """An abstract class that represents a specific HTTP endpoint in the Discord REST API.

    Has a single generic parameter (:obj:`~.GT`), which corresponds to the model class returned by
    the subclass' implementation of :meth:`parse_response`. This same generic parameter,
    with the same function, is also present in the direct (but still abstract) subclasses for GET, POST, PATCH,
    PUT and DELETE endpoints.

    For example, :class:`~.GetCurrentUserEndpoint` inherits :class:`~.GETEndpoint` [:class:`~.User`] (which, in turn,
    inherits ``Endpoint[User]``), meaning that, when raw data is received through that endpoint (GetCurrentUser),
    it should be parsed (using the parsing method defined on the GetCurrentUserEndpoint class) into a :class:`~.User`
    model instance.

    See Also:
        :class:`~.GETEndpoint`; :class:`~.POSTEndpoint`; :class:`~.PATCHEndpoint`; :class:`~.PUTEndpoint`;
        :class:`~.DELETEEndpoint`

    Attributes:
        method (:class:`~.HTTPMethod`): HTTP Method that this endpoint accepts (GET, POST, PUT, PATCH, or DELETE)
        parts (List[:class:`str`]): Each part (normally separated by /) that composes the endpoint URL
            (after the base API URL).
        headers (List[:class:`str`]): Extra headers to include for this endpoint when the request is done to the API.
        sent_data (Optional[:class:`aiohttp.FormData`]): Data to send in this endpoint (usually constructed in a
            subclass' ``__init__`` - defaults to ``None`` for no data).
        response (Optional[:class:`~.Response` [:obj:`~.GT`]]): Data (raw & parsed) received after a request was made
            using this Endpoint instance. This is only filled when a request is done
            successfully by :class:`~.Requester`.

    .. testsetup:: *

        from serpcord.rest.enums import HTTPMethod
        from serpcord.rest.endpoint.endpoint_abc import Endpoint
    """

    API_VERSION = API_VERSION
    """Discord API version being currently used in the library."""

    BASE_API_URL = BASE_API_URL
    """Base URL for all API requests."""

    def __init__(
        self, method: HTTPMethod, parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        self.method: HTTPMethod = method
        self.parts: List[str] = list(parts) if parts else []
        self.headers: Dict[str, str] = dict(headers) if headers else dict()

        self.sent_data: Optional[aiohttp.FormData] = None  # should be set by subclasses

        self.response: Optional[Response[GT]] = None  # will be set by Requester upon request execution

    @property
    def url(self) -> str:
        """Returns the full URL by joining (with /) all given parts of this endpoint, and appending them to the
        base API URL.

        Examples:
            .. testsetup:: endpointurl

                from serpcord.rest.endpoint.user import GetCurrentUserEndpoint
            .. doctest:: endpointurl

                >>> my_endpoint = GetCurrentUserEndpoint()
                >>> my_endpoint.parts
                ['users', '@me']
                >>> my_endpoint.url
                'https://discord.com/api/v9/users/@me'
        """
        return BASE_API_URL + ("/".join(self.parts))

    @abc.abstractmethod
    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> GT:
        """Abstract method for converting data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): The response data that should be converted to a model instance
                (the specific model depends on the Endpoint subclass, and is defined by the generic parameter ``GT``).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given response data.

        Raises:
            :exc:`APIDataParseException`: If the response data could not be properly parsed.
        """
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__qualname__} url={repr(self.url)}>"


class GETEndpoint(Endpoint[GT], abc.ABC):
    """Abstract class that represents a GET Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""

    method = HTTPMethod.GET  #: Always equal to :attr:`HTTPMethod.GET <.HTTPMethod.GET>`.

    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.GET, parts=parts, headers=headers)

    @abc.abstractmethod
    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> GT:
        """Abstract method for converting data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): The response data that should be converted to a model instance
                (the specific model depends on the Endpoint subclass, and is defined by the generic parameter ``GT``).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given response data.

        Raises:
            :exc:`APIDataParseException`: If the response data could not be properly parsed.
        """
        raise NotImplementedError


class POSTEndpoint(Endpoint[GT], abc.ABC):
    """Abstract class that represents a POST Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""

    method = HTTPMethod.POST  #: Always equal to :attr:`HTTPMethod.POST <.HTTPMethod.POST>`.

    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.POST, parts=parts, headers=headers)

    @abc.abstractmethod
    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> GT:
        """Abstract method for converting data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): The response data that should be converted to a model instance
                (the specific model depends on the Endpoint subclass, and is defined by the generic parameter ``GT``).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given response data.

        Raises:
            :exc:`APIDataParseException`: If the response data could not be properly parsed.
        """
        raise NotImplementedError


class PATCHEndpoint(Endpoint[GT], abc.ABC):
    """Abstract class that represents a PATCH Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""

    method = HTTPMethod.PATCH  #: Always equal to :attr:`HTTPMethod.PATCH <.HTTPMethod.PATCH>`.

    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.PATCH, parts=parts, headers=headers)

    @abc.abstractmethod
    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> GT:
        """Abstract method for converting data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): The response data that should be converted to a model instance
                (the specific model depends on the Endpoint subclass, and is defined by the generic parameter ``GT``).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given response data.

        Raises:
            :exc:`APIDataParseException`: If the response data could not be properly parsed.
        """
        raise NotImplementedError


class PUTEndpoint(Endpoint[GT], abc.ABC):
    """Abstract class that represents a PUT Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""

    method = HTTPMethod.PUT  #: Always equal to :attr:`HTTPMethod.PUT <.HTTPMethod.PUT>`.

    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.PUT, parts=parts, headers=headers)

    @abc.abstractmethod
    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> GT:
        """Abstract method for converting data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): The response data that should be converted to a model instance
                (the specific model depends on the Endpoint subclass, and is defined by the generic parameter ``GT``).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given response data.

        Raises:
            :exc:`APIDataParseException`: If the response data could not be properly parsed.
        """
        raise NotImplementedError


class DELETEEndpoint(Endpoint[GT], abc.ABC):
    """Abstract class that represents a DELETE Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""

    method = HTTPMethod.DELETE  #: Always equal to :attr:`HTTPMethod.DELETE <.HTTPMethod.DELETE>`.

    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.DELETE, parts=parts, headers=headers)

    @abc.abstractmethod
    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> GT:
        """Abstract method for converting data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): The response data that should be converted to a model instance
                (the specific model depends on the Endpoint subclass, and is defined by the generic parameter ``GT``).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given response data.

        Raises:
            :exc:`APIDataParseException`: If the response data could not be properly parsed.
        """
        raise NotImplementedError
