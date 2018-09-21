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
