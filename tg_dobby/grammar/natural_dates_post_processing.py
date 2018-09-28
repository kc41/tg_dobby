from typing import Tuple, NamedTuple, Union, List

from tg_dobby.grammar.model import (
    TemporalUnit,
    NamedInterval,

    TimesOfADayOption as ToaD,
    RelativeDayOption,
    UnitRelativePosition,
)

from tg_dobby.grammar.natural_dates import (
    Moment,
    RelativeInterval,
    DayOfWeek,
    RelativeDay,
    DayTime
)

from datetime import datetime, timedelta, time


##########################
# Errors & Clarifications
##########################

class TimeOfADayClarification(NamedTuple):
    time_of_a_day: ToaD


class DayTimeClarification(NamedTuple):
    day_time: Union[DayTime, time]


class DayOfWeekDiscriminatorClarification(NamedTuple):
    day_of_week_discriminator: UnitRelativePosition


ALL_CLARIFICATIONS_CLASSES = Union[
    TimeOfADayClarification,
    DayTimeClarification,
    DayOfWeekDiscriminatorClarification,
]


class ClarificationRequired(Exception):
    required_clarifications: Tuple[ALL_CLARIFICATIONS_CLASSES, ...]

    def __init__(self, *required_clarifications: ALL_CLARIFICATIONS_CLASSES):
        self.required_clarifications = tuple(required_clarifications)


class InvalidRelativeDateException(Exception):
    pass


########################
# Post-processing logic
########################

def get_day_time(day_time: DayTime, base: datetime = None) -> Tuple[int, int]:
    hour = day_time.hour
    minute = day_time.minute if day_time.minute else 0
    # second = day_time.second if day_time.second else 0

    am_pm = day_time.am_pm

    UNK_TIME_OF_A_DAY = f"Unknown time of a day: {am_pm}"

    # TODO FIX: realize more adequate AM/PM assumption mechanism
    def assume_am_pm():
        return ToaD.DAY

    # If format is HH:MM -> interpret as 24H format
    if day_time.strict_format:
        return hour, minute

    elif day_time.hour > 12:
        return hour, minute

    elif day_time.hour == 12:
        if am_pm in (ToaD.NIGHT, ToaD.EVENING):
            return 0, minute

        elif am_pm in (ToaD.MORNING, ToaD.DAY):
            return 12, minute

        if not am_pm:
            raise ClarificationRequired(TimeOfADayClarification(assume_am_pm()))

        else:
            raise InvalidRelativeDateException(UNK_TIME_OF_A_DAY)

    else:
        if am_pm in (ToaD.MORNING, ToaD.NIGHT):
            return hour, minute

        elif am_pm in (ToaD.DAY, ToaD.EVENING):
            return hour + 12, minute

        elif not am_pm:
            raise ClarificationRequired(TimeOfADayClarification(assume_am_pm()))

        else:
            raise InvalidRelativeDateException(UNK_TIME_OF_A_DAY)


def set_day_time(base: datetime, day_time: DayTime) -> datetime:
    hours, minutes = get_day_time(day_time=day_time, base=base)

    return base.replace(hour=hours, minute=minutes, second=0, microsecond=0)


# TODO FIX: request date clarification in 23:00 - 04:00 time range
def natural_relative_day_to_absolute_date(relative_day: RelativeDay, base: datetime) -> datetime:
    rd = relative_day.relative_day
    day_time = relative_day.day_time

    if rd == RelativeDayOption.TODAY:
        if day_time:
            return set_day_time(base, day_time)

        raise ClarificationRequired()

    elif rd == RelativeDayOption.TOMORROW:
        if day_time:
            return set_day_time(base, day_time) + timedelta(days=1)

        raise ClarificationRequired()

    elif rd == RelativeDayOption.THE_DAY_AFTER_TOMORROW:
        if day_time:
            return set_day_time(base, day_time) + timedelta(days=2)

        raise ClarificationRequired()

    else:
        raise InvalidRelativeDateException(f"Unknown relative day option: {rd}")


def natural_relative_interval_to_absolute_date(
        relative_interval: RelativeInterval,
        base: datetime,
        list_clarifications: List[ALL_CLARIFICATIONS_CLASSES] = None,
) -> datetime:
    unit = relative_interval.unit

    simple_units = {
        TemporalUnit.HOUR: lambda: base + timedelta(hours=relative_interval.amount if relative_interval.amount else 1),
        TemporalUnit.MINUTE: lambda: base + timedelta(
            hours=relative_interval.amount if relative_interval.amount else 1),
        NamedInterval.HALF_AN_HOUR: lambda: base + timedelta(minutes=30),
    }

    if unit in simple_units:
        return simple_units[unit]()

    elif unit == TemporalUnit.DAY:
        return base + timedelta(days=relative_interval.amount if relative_interval.amount else 1)
    else:
        raise InvalidRelativeDateException(f"Unknown unit/amount combination: {unit}, {relative_interval.amount}")


def get_absolute_date(
        moment: Moment,
        base: datetime = None,
        list_clarifications: List[ALL_CLARIFICATIONS_CLASSES] = None,
) -> datetime:
    if base is None:
        base = datetime.now()

    distance = moment.effective_date

    if isinstance(distance, RelativeInterval):
        return natural_relative_interval_to_absolute_date(relative_interval=distance, base=base)
    if isinstance(distance, RelativeDay):
        return natural_relative_day_to_absolute_date(relative_day=distance, base=base)
    if isinstance(distance, DayOfWeek):
        raise InvalidRelativeDateException(f"This type of relative date is not supported: {type(distance).__name__}")

    else:
        raise InvalidRelativeDateException(f"This type of relative date is not supported: {type(distance).__name__}")
