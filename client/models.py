from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from zoneinfo import ZoneInfo

from utils import get_level, get_level_current_xp, get_level_max_xp

utc = ZoneInfo("UTC")


@dataclass
class Tests:
    completed: int
    started: int
    time_typing: float

    @classmethod
    def from_api(cls, data: dict) -> Self:
        return cls(
            completed=data["completedTests"],
            started=data["startedTests"],
            time_typing=data["timeTyping"],
        )


@dataclass(eq=False)
class TestRecord:
    """Base class for LastTest and PersonalBest."""

    language: str
    test_mode: str
    mode_unit: int
    difficulty: str
    punctuation: bool
    numbers: bool
    wpm: float = field(compare=False)
    acc: float = field(compare=False)
    consistency: float = field(compare=False)
    test_time: datetime = field(compare=False)

    @classmethod
    def from_api(cls, data: dict) -> Self:
        """Create a TestRecord from API data."""
        return cls(
            language=data.get("language", "english"),
            test_mode=data["mode"],
            mode_unit=int(data["mode2"]),
            difficulty=data.get("difficulty", "normal"),
            punctuation=data.get("punctuation", False),
            numbers=data.get("numbers", False),
            wpm=data["wpm"],
            acc=data["acc"],
            consistency=data["consistency"],
            test_time=datetime.fromtimestamp(data["timestamp"] // 1000, tz=utc),
        )

    def __eq__(self, other: Any) -> bool:
        """Compare records based on the fingerprint fields."""
        if not isinstance(other, TestRecord):
            return NotImplemented

        fields = [
            "language",
            "test_mode",
            "mode_unit",
            "difficulty",
            "punctuation",
            "numbers",
        ]
        return all(getattr(self, f) == getattr(other, f) for f in fields)


@dataclass(eq=False)
class LastTest(TestRecord):
    """Class to store LastTest records, adds is_pb field to existing TestRecord fields."""

    is_pb: bool = field(init=False, compare=False)

    @classmethod
    def from_api(cls, data: dict) -> Self:
        """Create a LastTest instance from API data."""
        instance = super().from_api(data)
        instance.is_pb = data.get("isPb", False)
        return instance


@dataclass(eq=False)
class PersonalBest(TestRecord):
    """
    Class to store PersonalBest records.
    Use parse_personal_bests() to flatten the raw API data into a list of PersonalBest records.
    """

    @classmethod
    def parse_personal_bests(cls, data: dict) -> list[Self]:
        """Parse and flatten all personal bests into a list."""

        return [
            cls.from_api(record | {"mode": test_mode, "mode2": mode_unit})
            for test_mode, mode_units in data.items()  # Test modes are "time" or "words"
            for mode_unit, records in mode_units.items()  # Mode units are seconds or word count
            for record in records
        ]


@dataclass
class Profile:
    username: str
    date_joined: datetime
    xp: int
    tests: Tests
    personal_bests: list[PersonalBest]
    leader_boards: dict

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
            date_joined=datetime.fromtimestamp(data["addedAt"] // 1000, tz=utc),
            xp=data["xp"],
            tests=Tests.from_api(data["typingStats"]),
            personal_bests=PersonalBest.parse_personal_bests(data["personalBests"]),
            leader_boards=data["allTimeLbs"],
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
            last_result=datetime.fromtimestamp(data["lastResultTimestamp"] // 1000, tz=utc),
            current_length=data["length"],
            max_length=data["maxLength"],
        )


@dataclass
class Activity:
    daily_test_count: list[int]
    last_day: datetime

    @classmethod
    def from_api(cls, data: dict) -> Self:
        return cls(
            daily_test_count=[tests if tests else 0 for tests in data["testsByDays"]],
            last_day=datetime.fromtimestamp(data["lastDay"] // 1000, tz=utc),
        )
