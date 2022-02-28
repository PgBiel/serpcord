"""Endpoints related to users."""
import typing
import abc
from typing import Optional, Iterable, Generic

import aiohttp

from ...models.user import User
from .endpoint_abc import GETEndpoint, PATCHEndpoint


class GetCurrentUserEndpoint(GETEndpoint[User]):
    """API Endpoint for retrieving the current user (i.e., the bot itself). A GET to
    ``[BASE_API_URL]/users/@me``."""
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

    def __repr__(self):
        return f"{self.__class__.__qualname__}()"


class PatchCurrentUserEndpoint(PATCHEndpoint[User]):
    """API Endpoint for changing the current user (i.e., the bot itself). A PATCH to
    ``[BASE_API_URL]/users/@me``."""
    def __init__(self, *, username: Optional[str] = None, avatar: Optional[str] = None):  # TODO: Image Data type
        super().__init__(("users", "@me"), None)

    async def parse_response(self, response: aiohttp.ClientResponse) -> User:
        """Returns the modified user.

        See Also:
            :meth:`Endpoint.parse_response() <.Endpoint.parse_response>`
        """
        return await User.from_response(response)

    # def __repr__(self):
    #     return f"{self.__class__.__qualname__}(username=)"


# class GetCurrentUserGuildsEndpoint(GETEndpoint[List[Guild]])  # TODO: implement guilds

# class GetCurrentUserGuildMemberEndpoint(GETEndpoint[GuildMember])  # TODO: implement guildmember

# class LeaveGuildEndpoint(DELETEEndpoint[None])

# class CreateDMEndpoint(POSTEndpoint[DMChannel])  # TODO: DMChannel <- Channel

# class CreateGroupDMEndpoint(POSTEndpoint[GroupDMChannel])   # TODO: GroupDMChannel

# class GetUserConnectionsEndpoint(GETEndpoint[List[UserConnection]])  # TODO: UserConnection
