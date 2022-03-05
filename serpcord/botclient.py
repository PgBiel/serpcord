import asyncio
import typing
import aiohttp

from .rest.helpers import Response
from .rest.requester import Requester
from .utils.string import process_token
from .models import Snowflake, User
from .rest.endpoint.user import GetUserEndpoint
from typing import Union


class BotClient:
    """The starting point for Discord API interaction with a Bot, this class represents the bot's Client,
    and centralizes crucial data for its functioning.

    Attributes:
        token (:class:`str`): The bot's token. Note that the given token may be modified to be adapted to the
            Discord API, if it is not already valid (refer to
            :func:`utils.process_token() <.utils.string.process_token>` for details).
        session (:class:`aiohttp.ClientSession`): The bot's aiohttp session, used consistently across requests.
        requester (:class:`~.Requester`): The bot's :class:`~.Requester` instance, used for requests to the REST API.
    """
    def __init__(self, token: str):
        self.token: str = process_token(token)
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()  # TODO: move this to login(); fetch bot user
        self.requester: Requester = Requester(self.token, self, self.session, bind_session=False)

    async def fetch_user(self, user_id: Union[int, Snowflake]) -> User:
        """Fetches a Discord User from the API through their id.

        Args:
            user_id (Union[:class:`int`, :class:`~.Snowflake`]): The id of the user to be fetched.

        Returns:
            :class:`~.User`: The fetched user, if successful.

        Raises:
            :exc:`APIHttpNotFoundError`: If the user with the specified id was not found.
            :exc:`APIHttpStatusError`: If a bad HTTP status code was returned in general. (Something went wrong.)
        """
        endpoint = GetUserEndpoint(user_id)
        response: Response[User] = await self.requester.request_endpoint(endpoint)
        return response.parsed_response

    def __del__(self):
        if self and getattr(self, "session", None) and not getattr(self.session, "closed", True):
            asyncio.get_event_loop().run_until_complete(self.session.close())
