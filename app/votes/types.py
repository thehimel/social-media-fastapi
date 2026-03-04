from enum import Enum


class AddVoteResult(Enum):
    OK = "ok"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"


class RemoveVoteResult(Enum):
    OK = "ok"
    NOT_FOUND = "not_found"
