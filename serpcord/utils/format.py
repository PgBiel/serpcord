import re


def process_token(token: str):
    """Makes sure a given token is valid for usage within the Discord API.

    Args:
        token (:class:`str`): The token to be processed.

    Returns:
        :class:`str`: The modified, adapted token.

    Examples:
        .. testsetup::

            from serpcord.utils import process_token
        .. doctest::

            >>> process_token("Bot XXX")  # normal Bot token
            'Bot XXX'
            >>> process_token("Bearer XXX")  # normal Bearer token
            'Bearer XXX'
            >>> process_token("bot XXX")  # corrects case
            'Bot XXX'
            >>> process_token("beaREr XXX")  # corrects case
            'Bearer XXX'
            >>> process_token("XXX")  # defaults to Bot token
            'Bot XXX'
    """
    if token.startswith("Bot ") or token.startswith("Bearer "):
        return token
    elif re.match(r"^bot ", token, flags=re.I):
        return re.sub("^bot ", "Bot ", token, flags=re.I)
    elif re.match(r"^bearer ", token, flags=re.I):
        return re.sub("^bearer ", "Bearer ", token, flags=re.I)
    else:
        return f"Bot {token}"
