import aiohttp


class Requester:
    """Issues requests to the Discord API (REST)."""
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    # def request(self, ):