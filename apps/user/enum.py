from enum import Enum


class FollowStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"


class FollowKind(Enum):
    FOLLOWERS = "followers"
    FOLLOWINGS = "followings"
