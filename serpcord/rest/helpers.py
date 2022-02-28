import typing
import aiohttp
from typing import Generic, Optional, Any
from .enums import HTTPDataType


T = typing.TypeVar("T")


class HTTPSentData:
    """Helper class for :class:`~.Endpoint` subclasses to show what kind of data they will be sending to Discord.

    Attributes:
        data (:class:`aiohttp.FormData`): Data to be sent to Discord (over HTTP).
        data_type (:class:`~.HTTPDataType`): The type of the data being sent.
            (Defaults to :attr:`HTTPDataType.APPLICATION_JSON <.HTTPDataType.APPLICATION_JSON>` if unspecified.)
    """

    def __init__(self, data: aiohttp.FormData, data_type: HTTPDataType = HTTPDataType.APPLICATION_JSON):
        self.data: aiohttp.FormData = data
        self.data_type: HTTPDataType = data_type   # TODO: <--- might wanna delete this attr (seems useless)


class Response(Generic[T]):
    """Helper class for working with the results of :class:`~.Requester`.

    Attributes:
        status (:class:`int`): The HTTP status of the response. 2XX means OK.
        raw_response (:class:`bytes`): The raw response body.
        text_response (Optional[:class:`str`]): The response body as a string (if it was a text/json/... response).
        json_response (Optional[:class:`str`]): The response body as a Python object (if it was a JSON response).
        content_type (:class:`str`): The type of the response data.
        parsed_response (Optional[``T``]): The raw response parsed as a certain model instance (``T``) by an Endpoint.
            If no response was received (or expected) or parsing wasn't possible, this becomes ``None``.
    """
    def __init__(
        self,
        *, status: int,
        raw_response: Optional[bytes] = None,
        text_response: Optional[str] = None,
        json_response: Optional[Any] = None,
        content_type: str,
        parsed_response: Optional[T] = None
    ):
        self.status: int = status
        self.raw_response: Optional[bytes] = raw_response
        self.text_response: Optional[str] = text_response
        self.json_response: Optional[Any] = json_response
        self.parsed_response: Optional[T] = parsed_response
        self.content_type: str = content_type
