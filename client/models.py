from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from zoneinfo import ZoneInfo

from utils import get_level, get_level_current_xp, get_level_max_xp

utc = ZoneInfo("UTC")


@dataclass
class Profile:
    username: str
    date_joined: datetime
    xp: int

    level: int = field(init=False)
    level_current_xp: int = field(init=False)
    level_max_xp: int = field(init=False)

    def __post_init__(self):
        self.level = get_level(self.xp)
        self.level_current_xp = get_level_current_xp(self.xp)
        self.level_max_xp = get_level_max_xp(self.level)

    @classmethod
    def from_api(cls, data: dict) -> Self:
        return cls(
            username=data["name"],
            date_joined=datetime.fromtimestamp(data["addedAt"] / 1000, tz=utc),
            xp=data["xp"],
        )


@dataclass
class Streaks:
    last_result: datetime
    current_length: int
    max_length: int

    claimed: bool = field(init=False)

    def __post_init__(self):
        self.claimed = self.last_result.date() == datetime.now(tz=utc).date()

    @classmethod
    def from_api(cls, data: dict) -> Self:
        return cls(
            last_result=datetime.fromtimestamp(data["lastResultTimestamp"] / 1000, tz=utc),
            current_length=data["length"],
            max_length=data["maxLength"],
        )


@dataclass
class Stats:
    tests_completed: int
    tests_started: int
    time_typing: int

    @classmethod
    def from_api(cls, data: dict) -> Self:
        return cls(
            tests_completed=data["completedTests"],
            tests_started=data["startedTests"],
            time_typing=data["timeTyping"],
        )
