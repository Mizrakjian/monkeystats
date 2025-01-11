from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from zoneinfo import ZoneInfo

from utils import get_level, get_level_current_xp, get_level_max_xp


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
        self.level_current_xp = get_level_current_xp(self.level)
        self.level_max_xp = get_level_max_xp(self.level)

    @classmethod
    def from_api(cls, data: dict) -> Self:
        return cls(
            username=data["name"],
            date_joined=datetime.fromtimestamp(data["addedAt"] / 1000, tz=ZoneInfo("UTC")),
            xp=data["xp"],
        )
