"""Module for base endpoint classes (all abstract).

Hierarchy:
:class:`Endpoint` > (:class:`GETEndpoint`, :class:`POSTEndpoint`,
:class:`PATCHEndpoint`, :class:`PUTEndpoint`, :class:`DELETEEndpoint`)
"""
import typing
import abc
import aiohttp
from typing import Optional, Iterable, Any, List, Dict, TypeVar
from ..enums import HTTPMethod, HTTPSentDataType
from ..httpsentdata import HTTPSentData

API_VERSION = 9  #: Discord API version being currently used in the library.
BASE_API_URL = f"https://discord.com/api/v{API_VERSION}/"  #: Base URL for all API requests.

GT = TypeVar("GT")
"""Type parameter for parsed received data models for :class:`Endpoint` subclasses. I.e., for any Endpoint subclass,
the method :meth:`Endpoint.parse_raw_received_data_to` always converts raw data received from the API
(usually JSON) to an instance of ``GT``, whatever it may be (which depends on the subclass)."""
# TODO: examples (GT, ST)


class Endpoint(abc.ABC, typing.Generic[GT]):
    """An abstract class that represents a specific HTTP endpoint in the Discord REST API.

    Has a single generic parameter (:obj:`~.GT`), which corresponds to the model class returned by
    the subclass' implementation of :meth:`parse_raw_received_data_to`. This same generic parameter,
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
        sent_data (Optional[:class:`~.HTTPSentData`]): Data to send in this endpoint (usually constructed in a
            subclass' ``__init__`` - defaults to ``None`` for no data).
        received_data (Optional[:class:`str`]): Raw data received after a request was made
            using this Endpoint instance. This is only filled when a request is done
            successfully by :class:`~.Requester`.
        parsed_received_data (Optional[:obj:`~.GT`]): The model instance resulting from applying
            :meth:`parse_raw_received_data_to` to :attr:`received_data` after data is received.

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

        self.sent_data: Optional[HTTPSentData] = None  # should be set by subclasses

        self.received_data: Optional[str] = None
        # self.parsed_sent_data: Optional[ST] = None
        self.parsed_received_data: Optional[GT] = None

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
    def parse_raw_received_data_to(self, raw_data: str) -> GT:
        """Abstract method for converting raw data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            raw_data (:class:`str`): The raw data that should be converted to a model instance (whose class
                depends on the Endpoint subclass).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given raw data.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        raise NotImplementedError

    def on_data_receive(self, raw_data: str):
        """Method called when raw data is received as a response from the Discord API.
        Sets internal variables & etc.

        Args:
            raw_data (:class:`str`): The received raw data.
        """
        self.received_data = raw_data
        self.parsed_received_data = self.parse_raw_received_data_to(raw_data)

    def __repr__(self):
        method = repr(self.method)
        parts = repr(self.parts)
        headers = repr(self.headers)
        return f"{self.__class__.__qualname__}(method={method}, parts={parts}, headers={headers})"


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
    def parse_raw_received_data_to(self, raw_data: str) -> GT:
        """Abstract method for converting raw data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            raw_data (:class:`str`): The raw data that should be converted to a model instance (whose class
                depends on the Endpoint subclass).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given raw data.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        raise NotImplementedError

    def __repr__(self):
        parts = repr(self.parts)
        headers = repr(self.headers)
        return f"{self.__class__.__qualname__}(parts={parts}, headers={headers})"


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
    def parse_raw_received_data_to(self, raw_data: str) -> GT:
        """Abstract method for converting raw data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            raw_data (:class:`str`): The raw data that should be converted to a model instance (whose class
                depends on the Endpoint subclass).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given raw data.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        raise NotImplementedError

    def __repr__(self):
        parts = repr(self.parts)
        headers = repr(self.headers)
        return f"{self.__class__.__qualname__}(parts={parts}, headers={headers})"


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
    def parse_raw_received_data_to(self, raw_data: str) -> GT:
        """Abstract method for converting raw data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            raw_data (:class:`str`): The raw data that should be converted to a model instance (whose class
                depends on the Endpoint subclass).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given raw data.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        raise NotImplementedError

    def __repr__(self):
        parts = repr(self.parts)
        headers = repr(self.headers)
        return f"{self.__class__.__qualname__}(parts={parts}, headers={headers})"


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
    def parse_raw_received_data_to(self, raw_data: str) -> GT:
        """Abstract method for converting raw data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            raw_data (:class:`str`): The raw data that should be converted to a model instance (whose class
                depends on the Endpoint subclass).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given raw data.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        raise NotImplementedError

    def __repr__(self):
        parts = repr(self.parts)
        headers = repr(self.headers)
        return f"{self.__class__.__qualname__}(parts={parts}, headers={headers})"


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
    def parse_raw_received_data_to(self, raw_data: str) -> GT:
        """Abstract method for converting raw data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            raw_data (:class:`str`): The raw data that should be converted to a model instance (whose class
                depends on the Endpoint subclass).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given raw data.

        Raises:
            :exc:`APIDataParseException`: If the raw data could not be properly parsed.
        """
        raise NotImplementedError

    def __repr__(self):
        parts = repr(self.parts)
        headers = repr(self.headers)
        return f"{self.__class__.__qualname__}(parts={parts}, headers={headers})"
