import typing
import aiohttp

from serpcord.exceptions import APIJsonParsedTypeMismatchException
from .endpoint_abc import GETEndpoint
from typing import Optional, List
from serpcord.models.snowflake import Snowflake
from serpcord.utils.model import parse_json_list_response

if typing.TYPE_CHECKING:
    from serpcord.models.permissions import Role
    from serpcord.botclient import BotClient


class GetGuildRoles(GETEndpoint[List["Role"]]):
    """API Endpoint for fetching the list of roles in a guild. A GET to
    ``[BASE_API_URL]/guilds/[guild_id]/roles``.

    Args:
        guild_id (:class:`~.Snowflake`): The ID of the guild whose roles should be fetched.
    """
    def __init__(self, guild_id: Snowflake):
        super().__init__(["guilds", str(guild_id), "roles"], None)

    async def parse_response(self, client: "BotClient", response: aiohttp.ClientResponse) -> List["Role"]:
        """Returns the fetched list of :class:`~.Role` s, if successful."""
        from serpcord.models.permissions import Role
        return await parse_json_list_response(Role, client, response)
