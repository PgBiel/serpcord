"""Module for base endpoint classes (all abstract).

Hierarchy:
:class:`Endpoint` > (:class:`GETEndpoint`, :class:`POSTEndpoint`,
:class:`PATCHEndpoint`, :class:`PUTEndpoint`, :class:`DELETEEndpoint`)
"""
import typing
import abc
from typing import Optional, Iterable, Any, List, Dict, TypeVar
import aiohttp
from serpcord.rest.enums import HTTPMethod

API_VERSION = 9
BASE_API_URL = f"https://discord.com/api/v{API_VERSION}/"


GT = TypeVar("GT")
"""Type parameter for parsed received data models for :class:`Endpoint` subclasses. I.e., for any Endpoint subclass,
the method :meth:`Endpoint.parse_raw_received_data_to` always converts raw data received from the API
(usually JSON) to an instance of ``GT``, whatever it may be (which depends on the subclass)."""
# TODO: examples (GT, ST)

ST = TypeVar("ST")
"""Type parameter for data models that should be converted to raw data and sent to Discord API through
:class:`Endpoint` subclasses. I.e., for any Endpoint subclass, the method :meth:`Endpoint.get_raw_sending_data_from`
always takes an instance of ``ST`` - whatever it may be (which depends on the subclass) - and converts it to raw data
(usually JSON), which is then sent to the Discord API."""


class Endpoint(abc.ABC, typing.Generic[ST, GT]):
    """An abstract class that represents a specific endpoint in the Discord API.

    Attributes:
        method (:class:`~.HTTPMethod`): HTTP Method that this endpoint accepts (GET, POST, PUT, PATCH, or DELETE)
        parts (List[:class:`str`]): Each part (separated /) that composes the endpoint URL (after the base API URL).
        headers (List[:class:`str`]): Extra headers to include for this endpoint.

    See Also:
        :class:`~.GETEndpoint`; :class:`~.POSTEndpoint`; :class:`~.PATCHEndpoint`; :class:`~.PUTEndpoint`;
        :class:`~.DELETEEndpoint`

    .. testsetup:: *

        from serpcord.rest.enums import HTTPMethod
        from serpcord.rest.endpoint.endpoint import Endpoint
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
        self.sent_data: Optional[str] = None
        self.received_data: Optional[str] = None
        self.parsed_sent_data: Optional[ST] = None
        self.parsed_received_data: Optional[GT] = None

    # def append_part(self, part: str):
    #     self.parts.append(part)

    @property
    def url(self) -> str:
        """Returns the full URL by joining (with /) all given parts of this endpoint, and appending them to the
        base API URL.
        """
        # TODO: doctest using real example
        # Examples
        #     .. doctest::
        #
        #         >>> my_endpoint = Endpoint(HTTPMethod.POST, ("users", "@me", "channels"))
        #         >>> my_endpoint.url
        #         'https://discord.com/api/v9/users/@me/channels'
        return BASE_API_URL + ("/".join(self.parts))

    @abc.abstractmethod
    def get_raw_sending_data_from(self, model: ST) -> str:
        """Abstract method for converting a preexisting model to raw data to be sent to the Discord API
        through this endpoint (if needed).

        Args:
            model (:obj:`~.ST`): The model instance to be converted (whose class depends on the
                Endpoint subclass).

        Returns:
            :class:`str`: The resulting raw data extracted from the given model instance (which depends on the
            Endpoint - usually formatted in JSON).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_raw_received_data_to(self, raw_data: str) -> GT:
        """Abstract method for converting raw data received through the Discord API (usually JSON)
        to an instance of a model class.

        Args:
            raw_data (:class:`str`): The raw data that should be converted to a model instance (whose class
                depends on the Endpoint subclass).

        Returns:
            :obj:`~.GT`: The resulting model instance, constructed with the given raw data.
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
        return f"Endpoint(method={repr(self.method)}, parts={repr(self.parts)})"


class GETEndpoint(typing.Generic[ST, GT], Endpoint[ST, GT], abc.ABC):
    """Abstract class that represents a GET Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""
    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.GET, parts=parts, headers=headers)


# class SendingEndpoint(abc.ABC, Endpoint, typing.Generic[T]):
#     def __init__(
#         self,
#         method: HTTPMethod, parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
#     ):
#         self.parsed_data: Optional[T] = None
#         super().__init__(method=method, parts=parts, headers=headers)
#
#     @abc.abstractmethod
#     def parse_sent_data(self, data: T) -> str:
#         raise NotImplementedError()


class POSTEndpoint(typing.Generic[ST, GT], Endpoint[ST, GT], abc.ABC):
    """Abstract class that represents a POST Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""
    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.POST, parts=parts, headers=headers)  # parse_sent_data remains abstract


class PATCHEndpoint(typing.Generic[ST, GT], Endpoint[ST, GT], abc.ABC):
    """Abstract class that represents a PATCH Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""
    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.PATCH, parts=parts, headers=headers)  # parse_sent_data remains abstract


class PUTEndpoint(typing.Generic[ST, GT], Endpoint[ST, GT], abc.ABC):
    """Abstract class that represents a PUT Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""
    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.PUT, parts=parts, headers=headers)  # parse_sent_data remains abstract


class DELETEEndpoint(typing.Generic[ST, GT], Endpoint[ST, GT], abc.ABC):
    """Abstract class that represents a DELETE Endpoint in the Discord API.
    Its abstract methods are the same as those of :class:`Endpoint`."""
    def __init__(
        self,
        parts: Optional[Iterable[str]] = None, headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(method=HTTPMethod.DELETE, parts=parts, headers=headers)
