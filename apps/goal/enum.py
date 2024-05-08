from enum import Enum


class ShowScope(Enum):
    ME = "me"
    FOLLWERS = "followers"
    ALL = "all"


class GoalStatus(Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"