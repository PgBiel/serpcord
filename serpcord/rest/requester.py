import aiohttp
import typing
import asyncio
from typing import Generic, Optional, ClassVar

from ..utils.string import process_token
from .enums import HTTPDataType
from .helpers import Response
from .endpoint.endpoint_abc import Endpoint
from serpcord.exceptions.httpexc import APIHttpStatusError, APIHttpBadRequestError, APIHttpNotFoundError, \
    APIHttpRatelimitedError, APIHttpUnauthorizedError, APIHttpForbiddenError, APIHttpUserSideError, \
    APIHttpInternalServerError, APIHttpBadGatewayError, APIHttpServiceUnavailableError, APIHttpGatewayTimeoutError, \
    APIHttpServerSideError

T = typing.TypeVar("T")

if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient


class Requester:
    """Issues requests to the Discord API (REST).

    Attributes:
        token (:class:`str`): The client's token.
        client (:class:`~.BotClient`): The bot's active client instance, which was used to create this instance
            of Requester.
        session (:class:`aiohttp.ClientSession`): The client's session, for requests.
        bind_session (:class:`bool`): If ``True``, the given session will be closed when the
            ``Requester`` instance is destroyed. (``False`` by default.)

    .. testsetup:: *

        import aiohttp
        from serpcord.rest.requester import Requester
        sample_requester = Requester("", aiohttp.ClientSession(), bind_session=True)
    """

    #: The library's user agent header.
    USER_AGENT: ClassVar[str] = "serpcord (https://github.com/PgBiel/serpcord, 0.0.1a)"

    def __init__(self, token: str, client: "BotClient", session: aiohttp.ClientSession, *, bind_session: bool = False):
        self.token = process_token(token)
        self.client = client
        # session.headers.add
        session.headers.add("Authorization", self.token)
        session.headers.add("User Agent", Requester.USER_AGENT)
        self.session = session
        self.bind_session = bind_session

    def __del__(self):
        if (
            self
            and getattr(self, "bind_session", False)
            and getattr(self, "session", None)
            and not getattr(self.session, "closed", True)
        ):
            asyncio.get_event_loop().run_until_complete(self.session.close())

    async def request_endpoint(self, endpoint: Endpoint[T]) -> Response[T]:  # TODO: endpoint with async parsing; imgs
        """Sends a request to the Discord REST API through an :class:`~.Endpoint` [``T``] instance,
        and stores and returns the results in the form of a :class:`~.Response` [``T``] instance.

        Note that the generic parameter ``T`` here corresponds to the expected model type after the response is parsed.

        Args:
            endpoint (:class:`~.Endpoint` [``T``]): The endpoint instance that indicates to where the request will go,
                along with the method, headers and other data being sent.

        Returns:
            :class:`~.Response` [``T``]: A :class:`~.Response` object with the status of the request (2XX is OK),
            its content type, its raw body, text body, JSON-parsed body, and the parsed model provided by the
            Endpoint object.
        """
        headers = {
            # "Authorization": self.token,  # already added on __init__
            **endpoint.headers
        }
        async with self.session.request(
            endpoint.method.value.lower(), endpoint.url, headers=headers,
            data=endpoint.sent_data or None
        ) as resp:
            try:
                resp.raise_for_status()
            except aiohttp.ClientResponseError as e:
                raise Requester._convert_http_error(e) from e

            content_type = resp.content_type
            parsed_resp: T = await endpoint.parse_response(self.client, resp)

            raw_resp: bytes = await resp.read()
            text_resp: Optional[str] = None
            json_resp: Optional[typing.Any] = None
            if content_type.startswith("text/"):
                text_resp = await resp.text()
            elif content_type == HTTPDataType.APPLICATION_JSON.value:
                text_resp = await resp.text()
                json_resp = await resp.json()

            response = Response(
                status=resp.status,
                raw_response=raw_resp, text_response=text_resp, json_response=json_resp,
                content_type=content_type, parsed_response=parsed_resp
            )
            endpoint.response = response
            return response

    @staticmethod
    def _convert_http_error(error: aiohttp.ClientResponseError) -> APIHttpStatusError:
        """Converts a status-related response error to an instance of one of
        :mod:`the library's custom HTTP Exceptions <serpcord.exceptions.httpexc>`.

        Args:
            error (:class:`aiohttp.ClientResponseError`): The error to be converted.

        Returns:
            :class:`~.APIHttpStatusError`: The converted error.
        """
        status = int(error.status)
        request_info = error.request_info
        history = error.history
        headers = error.headers
        message = error.message
        init_args: typing.Any = dict(
            request_info=request_info, history=history, status=status, headers=headers, message=message
        )

        if status == 400:
            return APIHttpBadRequestError(**init_args)
        if status == 404:
            return APIHttpNotFoundError(**init_args)
        if status == 429:
            return APIHttpRatelimitedError(**init_args)
        if status == 401:
            return APIHttpUnauthorizedError(**init_args)
        if status == 403:
            return APIHttpForbiddenError(**init_args)
        if 400 <= status < 500:  # not any of the above, but still in the 400s
            return APIHttpUserSideError(**init_args)

        if status == 500:
            return APIHttpInternalServerError(**init_args)
        if status == 502:
            return APIHttpBadGatewayError(**init_args)
        if status == 503:
            return APIHttpServiceUnavailableError(**init_args)
        if status == 504:
            return APIHttpGatewayTimeoutError(**init_args)
        if 500 <= status < 600:  # not any of the above, but still in 500s (there isn't 600+, but, for typing's sake...)
            return APIHttpServerSideError(**init_args)

        return APIHttpStatusError(**init_args)  # catch-all
