class SerpcordException(Exception):
    """Base class for all custom exceptions possibly raised by this library."""
    pass

class APIRequestException(SerpcordException):
    """Any exception that may occur when requesting to the API."""
    pass
