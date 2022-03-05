import aiohttp
from .serpcordexc import APIRequestException


class APIHttpStatusError(aiohttp.ClientResponseError, APIRequestException):
    """Indicates we received a bad HTTP status (non-200) from Discord."""
    pass


class APIHttpUserSideError(APIHttpStatusError):
    """Indicates a status in the 400 range was received, meaning an error occurred due to issues in the request
    made by the user (and not due to the server)."""
    pass


class APIHttpBadRequestError(APIHttpUserSideError):
    """Indicates the request sent to the API was malformed or did not attend to the expectations of that endpoint."""
    status = 400
    pass


class APIHttpNotFoundError(APIHttpUserSideError):
    """Indicates there was an attempt to request an unexistent object, or endpoint."""
    status = 404
    pass


class APIHttpRatelimitedError(APIHttpUserSideError):
    """Indicates the bot was ratelimited due to requesting to the same endpoint too frequently."""
    status = 429
    pass


class APIHttpUnauthorizedError(APIHttpUserSideError):
    """Indicates there was an attempt to perform an option without specifying a valid API token."""
    status = 401
    pass


class APIHttpForbiddenError(APIHttpUserSideError):
    """Indicates there was an attempt to perform an action or retrieve information to which the bot has no access."""
    status = 403
    pass


class APIHttpServerSideError(APIHttpStatusError):
    """Indicates a status in the 500 range was received, meaning an error occured due to issues with Discord's
    servers."""
    pass


class APIHttpInternalServerError(APIHttpServerSideError):
    """Indicates an unknown internal server error occurred at Discord's side while attempting to respond to
    our request."""
    status = 500
    pass


class APIHttpBadGatewayError(APIHttpServerSideError):
    """Indicates there was an error while resolving the gateway the bot would connect to."""
    status = 502
    pass


class APIHttpServiceUnavailableError(APIHttpServerSideError):
    """Indicates Discord's services are temporarily down or overloaded."""
    status = 503
    pass


class APIHttpGatewayTimeoutError(APIHttpServerSideError):
    """Indicates the connection to the gateway timed out."""
    status = 504
    pass
