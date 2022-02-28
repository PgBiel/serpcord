import aiohttp
import typing
import re
import asyncio
from .endpoint.endpoint_abc import Endpoint


T = typing.TypeVar("T")


# class Response(typing.Generic[T]):
#


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
    def __init__(self, token: str, session: aiohttp.ClientSession, *, bind_session: bool = False):
        self.token = ""
        self.process_token(token)

        # session.headers.add
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

    # def request_endpoint(self, endpoint: Endpoint[T]) :
