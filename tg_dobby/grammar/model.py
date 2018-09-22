import enum


class TemporalUnit(enum.Enum):
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class NamedInterval(enum.Enum):
    HALF_AN_HOUR = "HALF_AN_HOUR"


class RelativeDayOption(enum.Enum):
    TOMORROW = "TOMORROW"
    YESTERDAY = "YESTERDAY"
    THE_DAY_AFTER_TOMORROW = "THE_DAY_AFTER_TOMORROW"
    TODAY = "TODAY"


class TimesOfADayOption(enum.Enum):
    DAY = "DAY"
    MORNING = "MORNING"
    EVENING = "EVENING"
    NIGHT = "NIGHT"


class UnitRelativePosition(enum.Enum):
    THIS = "THIS"
    NEXT = "NEXT"
    CLOSEST = "CLOSEST"
