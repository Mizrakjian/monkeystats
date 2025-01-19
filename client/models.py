from dataclasses import asdict, dataclass, field
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


@dataclass
class TestRecord:
    language: str
    test_mode: str
    mode_unit: int
    difficulty: str
    punctuation: bool
    numbers: bool
    wpm: float
    acc: float
    consistency: float
    test_time: datetime

    @classmethod
    def from_api(cls, data: dict, context: dict | None = None) -> Self:
        """Create a TestRecord from API data, with optional context overrides."""
        if context is None:
            context = {}
        merged_data = data | context  # Merge original data with overrides
        return cls(
            language=merged_data.get("language", "english"),
            test_mode=merged_data["mode"],
            mode_unit=int(merged_data["mode2"]),
            difficulty=merged_data.get("difficulty", "normal"),
            punctuation=merged_data.get("punctuation", False),
            numbers=merged_data.get("numbers", False),
            wpm=merged_data["wpm"],
            acc=merged_data["acc"],
            consistency=merged_data["consistency"],
            test_time=datetime.fromtimestamp(merged_data["timestamp"] / 1000, tz=utc),
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
        return all(getattr(self, field) == getattr(other, field) for field in fields)


@dataclass(eq=False)
class LastTest(TestRecord):
    is_pb: bool

    @classmethod
    def from_api(cls, data: dict) -> Self:
        """Create a LastTest instance from API data."""
        # Parse shared fields from the parent
        shared_fields = asdict(TestRecord.from_api(data))
        # Add subclass-specific fields
        return cls(is_pb=data.get("isPb", False), **shared_fields)


@dataclass(eq=False)
class PersonalBest(TestRecord):
    @classmethod
    def from_api(cls, data: dict, language: str, test_mode: str, mode_unit: int) -> Self:
        """Create a PersonalBest instance from a flattened API record."""
        return super().from_api(data, {"language": language, "mode": test_mode, "mode2": mode_unit})

    @classmethod
    def parse_personal_bests(cls, data: dict) -> list[Self]:
        """Parse and flatten all personal bests into a list."""
        personal_bests = []
        # Iterate over test modes (e.g., "time", "words")
        for test_mode, mode_units in data.items():
            # Iterate over mode units (e.g., number of seconds or words)
            for mode_unit, records in mode_units.items():
                # Parse each record
                for record in records:
                    # Extract language from the record, default to "english"
                    language = record.get("language", "english")
                    personal_bests.append(cls.from_api(record, language, test_mode, mode_unit))
        return personal_bests


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
            date_joined=datetime.fromtimestamp(data["addedAt"] / 1000, tz=utc),
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
            last_result=datetime.fromtimestamp(data["lastResultTimestamp"] / 1000, tz=utc),
            current_length=data["length"],
            max_length=data["maxLength"],
        )


@dataclass
class Activity:
    daily_test_count: list[int | None]
    last_day: datetime

    @classmethod
    def from_api(cls, data: dict) -> Self:
        return cls(
            daily_test_count=[tests if tests else 0 for tests in data["testsByDays"]],
            last_day=datetime.fromtimestamp(data["lastDay"] / 1000, tz=utc),
        )
