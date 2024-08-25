from enum import Enum


class ShowScope(Enum):
    ALL = "all"
    FOLLWERS = "followers"
    GROUP = "group"
    ME = "me"


class GoalStatus(Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class ReactionType(Enum):
    COMMENT = "comment"
    EMOTICON = "imoticon"
