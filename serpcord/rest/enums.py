from enum import Enum


class HTTPMethod(Enum):
    """Lists possible HTTP requesting methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"HTTPMethod.{self.name}"
