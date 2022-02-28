import aiohttp
import typing
import re
import asyncio
import inspect
from typing import Generic, Optional, ClassVar

from .enums import HTTPDataType
from .helpers import Response
from .endpoint.endpoint_abc import Endpoint


T = typing.TypeVar("T")


class Requester:
    """Issues requests to the Discord API (REST).

    Attributes:
        token (:class:`str`): The client's token.
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

    def __init__(self, token: str, session: aiohttp.ClientSession, *, bind_session: bool = False):
        self.token = ""
        self.process_token(token)

        # session.headers.add
        session.headers.add("Authorization", self.token)
        session.headers.add("User Agent", Requester.USER_AGENT)
        self.session = session
        self.bind_session = bind_session

    def process_token(self, token: str):
        """Makes sure a given token is valid for usage within the Discord API, and saves it as `self.token`.

        Args:
            token (:class:`str`): The token that this :class:`Requester` instance should be using to be processed.

        Examples:
            .. doctest::

                >>> assert isinstance(sample_requester, Requester)
                >>> sample_requester.process_token("Bot XXX")
                >>> sample_requester.token
                'Bot XXX'
                >>> sample_requester.process_token("Bearer XXX")
                >>> sample_requester.token
                'Bearer XXX'
                >>> sample_requester.process_token("bot XXX")
                >>> sample_requester.token
                'Bot XXX'
                >>> sample_requester.process_token("beaREr XXX")
                >>> sample_requester.token
                'Bearer XXX'
                >>> sample_requester.process_token("XXX")
                >>> sample_requester.token
                'Bot XXX'
                >>> other_requester = Requester("YYY", aiohttp.ClientSession(), bind_session=True)
                >>> other_requester.token  # also applied on instantiation
                'Bot YYY'
        """
        if token.startswith("Bot ") or token.startswith("Bearer "):
            self.token = token
        elif re.match(r"^bot ", token, flags=re.I):
            self.token = re.sub("^bot ", "Bot ", token, flags=re.I)
        elif re.match(r"^bearer ", token, flags=re.I):
            self.token = re.sub("^bearer ", "Bearer ", token, flags=re.I)
        else:
            self.token = f"Bot {token}"

    def __del__(self):
        if self.bind_session:
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
            data=endpoint.sent_data.data if endpoint.sent_data else None
        ) as resp:
            content_type = resp.content_type
            parsed_resp: T = await endpoint.parse_response(resp)

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
