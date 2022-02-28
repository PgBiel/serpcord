from .enums import HTTPSentDataType


class HTTPSentData:
    """Helper class for :class:`~.Endpoint` subclasses to show what kind of data they will be sending to Discord.

    Attributes:
        data (:class:`str`): Raw data to be sent to Discord (over HTTP).
        data_type (:class:`~.HTTPSentDataType`): The type of the data being sent.
            (Defaults to :attr:`HTTPSentDataType.APPLICATION_JSON <.HTTPSentDataType.APPLICATION_JSON>` if unspecified.)
    """

    def __init__(self, data: str, data_type: HTTPSentDataType = HTTPSentDataType.APPLICATION_JSON):
        self.data: str = data
        self.data_type: HTTPSentDataType = data_type
