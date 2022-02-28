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


class CDNImageFormats(Enum):
    """An :class:`~enum.Enum` listing possible image formats (mapped to their file extensions)
    available for retrieval from the Discord CDN.

    .. testsetup:: *

        from serpcord.rest.enums import *
    """
    JPG = "jpg"  # technically JPEG, but, for the sake of being type-strict...
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"
    LOTTIE = "json"

    @property
    def file_extension(self):
        """Returns this image format as a file extension (preceded by a dot ``.``)

        Examples:
            .. doctest::

                >>> CDNImageFormats.JPEG.value
                'jpeg'
                >>> CDNImageFormats.JPEG.file_extension
                '.jpeg'
                >>> CDNImageFormats.LOTTIE.file_extension
                '.json'
                >>> CDNImageFormats.GIF.file_extension
                '.gif'
        """
        return f".{self.value}"


class HTTPSentDataType(Enum):
    """An :class:`~enum.Enum` listing possible types of data to be sent to the Discord API."""

    APPLICATION_JSON = "application/json"
