"""Endpoints related to users."""
import typing
import abc
import io
from typing import Optional, Iterable, Generic, Union

import aiohttp

from ..helpers import Response
from .endpoint_abc import GETEndpoint, PATCHEndpoint
from serpcord.models.snowflake import Snowflake
from serpcord.utils.typeutils import SERPCORD_DEFAULT, OrDefault, OptionalOrDefault


if typing.TYPE_CHECKING:
    from serpcord.botclient import BotClient
    from serpcord.models.user import BotUser, User


class GetCurrentUserEndpoint(GETEndpoint["BotUser"]):
    """API Endpoint for retrieving the current user (i.e., the bot itself). A GET to
    ``[BASE_API_URL]/users/@me``."""
    response: Optional[Response["BotUser"]]  #: Response object containing the bot's user (if successful).

    def __init__(self):
        super().__init__(("users", "@me"), None)

    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> "BotUser":
        """Returns the current running bot's :class:`~.BotUser` by parsing response data received from Discord.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): Response data received from Discord to parse.

        Returns:
            :class:`~.BotUser`: The :class:`~.BotUser` instance that resulted from parsing the response data, which
            corresponds to the current user (i.e. the bot's user).

        See Also:
            :meth:`Endpoint.parse_response() <.Endpoint.parse_response>`
        """
        from serpcord.models.user import BotUser
        return await BotUser._from_response(client, response)


class GetUserEndpoint(GETEndpoint["User"]):
    """API Endpoint for retrieving a user. A GET to
    ``[BASE_API_URL]/users/:user_id``.

    Args:
        user_id (Union[:class:`int`, :class:`~.Snowflake`): ID of the user to be fetched.
    """
    response: Optional[Response["User"]]  #: Response object containing the retrieved user (if successful).

    def __init__(self, user_id: Union[int, Snowflake]):
        super().__init__(("users", str(int(user_id))), None)

    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> "User":
        """Returns the current running bot's :class:`~.BotUser` by parsing response data received from Discord.

        Args:
            client (:class:`~.BotClient`): The bot's active client instance.
            response (:class:`aiohttp.ClientResponse`): Response data received from Discord to parse.

        Returns:
            :class:`~.BotUser`: The :class:`~.BotUser` instance that resulted from parsing the response data, which
            corresponds to the current user (i.e. the bot's user).

        See Also:
            :meth:`Endpoint.parse_response() <.Endpoint.parse_response>`
        """
        from serpcord.models.user import User
        return await User._from_response(client, response)


class PatchCurrentUserEndpoint(PATCHEndpoint["BotUser"]):
    """API Endpoint for changing the current user (i.e., the bot itself). A PATCH to
    ``[BASE_API_URL]/users/@me``.

    Args:
        username (:class:`str`, optional): The bot user's new username. (Don't specify to leave unchanged.)
        avatar (Optional[Union[:class:`bytes`, :class:`io.IOBase`]], optional): The bot user's new avatar image.
            (Don't specify to leave unchanged; specify ``None`` to remove an existing avatar.)
    """
    response: Optional[Response["BotUser"]]  #: Response object containing the modified user (if successful).

    def __init__(
        self,
        *, username: OrDefault[str] = SERPCORD_DEFAULT,
        avatar: OptionalOrDefault[Union[bytes, io.IOBase]] = SERPCORD_DEFAULT
    ):
        super().__init__(("users", "@me"), None)  # TODO: Image Data type

        self.sent_data = aiohttp.FormData()

        if username != SERPCORD_DEFAULT:
            self.sent_data.add_field("username", username)
        if avatar != SERPCORD_DEFAULT:
            self.sent_data.add_field("avatar", avatar)

    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> "BotUser":
        """Returns the modified bot user.

        See Also:
            :meth:`Endpoint.parse_response() <.Endpoint.parse_response>`
        """
        from serpcord.models.user import BotUser
        return await BotUser._from_response(client, response)


# class GetCurrentUserGuildsEndpoint(GETEndpoint[List[Guild]])  # TODO: implement guilds

# class GetCurrentUserGuildMemberEndpoint(GETEndpoint[GuildMember])  # TODO: implement guildmember

# class LeaveGuildEndpoint(DELETEEndpoint[None])

# class CreateDMEndpoint(POSTEndpoint[DMChannel])  # TODO: DMChannel <- Channel

# class CreateGroupDMEndpoint(POSTEndpoint[GroupDMChannel])   # TODO: GroupDMChannel

# class GetUserConnectionsEndpoint(GETEndpoint[List[UserConnection]])  # TODO: UserConnection
