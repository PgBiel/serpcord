"""Endpoints related to users."""
import typing
import abc
import io
from typing import Optional, Iterable, Generic, Union

import aiohttp

from ..helpers import Response
from ...models.user import User
from .endpoint_abc import GETEndpoint, PATCHEndpoint


class GetCurrentUserEndpoint(GETEndpoint[User]):
    """API Endpoint for retrieving the current user (i.e., the bot itself). A GET to
    ``[BASE_API_URL]/users/@me``."""
    response: Optional[Response[User]]  #: Response object containing the bot's user (if successful).

    def __init__(self):
        super().__init__(("users", "@me"), None)

    async def parse_response(self, response: aiohttp.ClientResponse) -> User:
        """Returns the current :class:`~.User` by parsing response data received from Discord.

        Args:
            response (:class:`aiohttp.ClientResponse`): Response data received from Discord to parse.

        Returns:
            :class:`~.User`: The :class:`~.User` instance that resulted from parsing the response data, which should
            correspond to the current user (i.e. the bot's user).

        See Also:
            :meth:`Endpoint.parse_response() <.Endpoint.parse_response>`
        """
        return await User.from_response(response)


class PatchCurrentUserEndpoint(PATCHEndpoint[User]):
    """API Endpoint for changing the current user (i.e., the bot itself). A PATCH to
    ``[BASE_API_URL]/users/@me``.

    Args:
        username (Optional[:class:`str`]): The bot user's new username. (``None`` to leave unchanged.)
        avatar (Optional[Union[:class:`bytes`, :class:`io.IOBase`]]): The bot user's new avatar image.
            (``None`` to leave unchanged.)
    """
    response: Optional[Response[User]]  #: Response object containing the modified user (if successful).

    def __init__(self, *, username: Optional[str] = None, avatar: Optional[Union[bytes, io.IOBase]] = None):
        super().__init__(("users", "@me"), None)  # TODO: Image Data type

        self.sent_data = aiohttp.FormData()

        if username is not None:
            self.sent_data.add_field("username", username)
        if avatar is not None:
            self.sent_data.add_field("avatar", avatar)

    async def parse_response(self, response: aiohttp.ClientResponse) -> User:
        """Returns the modified user.

        See Also:
            :meth:`Endpoint.parse_response() <.Endpoint.parse_response>`
        """
        return await User.from_response(response)


# class GetCurrentUserGuildsEndpoint(GETEndpoint[List[Guild]])  # TODO: implement guilds

# class GetCurrentUserGuildMemberEndpoint(GETEndpoint[GuildMember])  # TODO: implement guildmember

# class LeaveGuildEndpoint(DELETEEndpoint[None])

# class CreateDMEndpoint(POSTEndpoint[DMChannel])  # TODO: DMChannel <- Channel

# class CreateGroupDMEndpoint(POSTEndpoint[GroupDMChannel])   # TODO: GroupDMChannel

# class GetUserConnectionsEndpoint(GETEndpoint[List[UserConnection]])  # TODO: UserConnection
