
from enum import Enum


class ActivityStatus(str, Enum):
    """
    Defines the lifecycle status of an Activity.
    """

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

