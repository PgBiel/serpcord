import aiohttp
from .rest.requester import Requester
from .utils import process_token


class BotClient:
    """The starting point for Discord API interaction with a Bot, this class represents the bot's Client,
    and centralizes crucial data for its functioning.

    Attributes:
        token (:class:`str`): The bot's token. Note that the given token may be modified to be adapted to the
            Discord API, if it is not already valid (refer to
            :func:`utils.process_token() <.utils.format.process_token>` for details).
        session (:class:`aiohttp.ClientSession`): The bot's aiohttp session, used consistently across requests.
        requester (:class:`~.Requester`): The bot's :class:`~.Requester` instance, used for requests to the REST API.
    """
    def __init__(self, token: str):
        self.token: str = process_token(token)
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()  # TODO: move this to login()
        self.requester: Requester = Requester(self.token, self.session, bind_session=False)

    def __del__(self):
        self.session.close()
