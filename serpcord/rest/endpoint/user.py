"""Endpoints related to users."""
import typing
import abc
from typing import Optional, Iterable, Generic
from ...models.user import User
from .endpoint_abc import GETEndpoint, PATCHEndpoint


class GetCurrentUserEndpoint(GETEndpoint[User]):
    """API Endpoint for retrieving the current user (i.e., the bot itself). A GET to [BASE_API_URL]/users/@me."""
    def __init__(self):
        super().__init__(("users", "@me"), None)

    def parse_raw_received_data_to(self, data: str) -> User:
        return User.from_raw_data(data)


class PatchCurrentUserEndpoint(PATCHEndpoint[User]):
    """API Endpoint for changing the current user (i.e., the bot itself). A PATCH to [BASE_API_URL]/users/@me."""
    def __init__(self, *, username: Optional[str] = None, avatar: Optional[str] = None):  # TODO: Image Data type
        super().__init__(("users", "@me"), None)

    def parse_raw_received_data_to(self, data: str) -> User:
        """Returns the modified user."""
        return User.from_raw_data(data)


# class GetCurrentUserGuildsEndpoint(GETEndpoint[List[Guild]])  # TODO: implement guilds

# class GetCurrentUserGuildMemberEndpoint(GETEndpoint[GuildMember])  # TODO: implement guildmember

# class LeaveGuildEndpoint(DELETEEndpoint[None])

# class CreateDMEndpoint(POSTEndpoint[DMChannel])  # TODO: DMChannel <- Channel

# class CreateGroupDMEndpoint(POSTEndpoint[GroupDMChannel])   # TODO: GroupDMChannel

# class GetUserConnectionsEndpoint(GETEndpoint[List[UserConnection]])  # TODO: UserConnection
