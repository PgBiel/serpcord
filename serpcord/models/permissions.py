from .apimodel import JsonAPIModel
from .snowflake import Snowflake
from .enums import PermissionFlags, PermissionOverwriteType
from serpcord.utils.model import init_model_from_mapping_json_data
from typing import Mapping, Any, Optional


class PermissionOverwrite(JsonAPIModel[Mapping[str, Any]]):
    """Represents a Permission Overwrite for a member or role in a channel, allowing or denying a permission
    for the target (either a user - if the target is a user - or all users with a certain role - if the target
    is a role).

    Attributes:
        target_id (:class:`~.Snowflake`): ID of the target of this Permission Overwrite (user or role).
        overwrite_type (:class:`~.PermissionOverwriteType`): The type of the target of this Permission Overwrite
            (:attr:`~.PermissionOverwriteType.USER` or :attr:`~.PermissionOverwriteType.ROLE`).
        allow (:class:`~.PermissionFlags`): The permissions that this overwrite grants to the target in the channel
            the overwrite was created in.
        deny (:class:`~.PermissionFlags`): The permissions that this overwrite revokes from the target in the channel
            the overwrite was created in.
    """

    def __init__(
        self, target_id: Snowflake, overwrite_type: PermissionOverwriteType,
        *, allow: PermissionFlags = PermissionFlags.NONE, deny: PermissionFlags = PermissionFlags.NONE
    ):
        self.target_id: Snowflake = target_id
        self.overwrite_type: PermissionOverwriteType = overwrite_type
        self.allow: PermissionFlags = allow
        self.deny: PermissionFlags = deny

    @classmethod
    def from_json_data(cls, json_data: Mapping[str, Any]):
        return init_model_from_mapping_json_data(
            cls, json_data, rename=dict(id="target_id", type="overwrite_type"),
            type_check_types=True
        )

    def __repr__(self):
        return f"{self.__class__.__qualname__}(target_id={self.target_id!r}, overwrite_type={self.overwrite_type!r}, \
allow={self.allow!r}, deny={self.deny!r})"
