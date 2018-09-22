from typing import NamedTuple, Tuple

from tg_dobby.grammar.model import (
    TemporalUnit,
    NamedInterval,

    TimesOfADayOption as ToaD,
)

from tg_dobby.grammar.natural_dates import (
    Moment,
    RelativeInterval,
    DayOfWeek,
    RelativeDay,
    DayTime
)

from datetime import datetime, timedelta, time


class DateClarification(NamedTuple):
    time: time = None
    pm: bool = None


class ClarificationRequired(Exception):
    pass


class InvalidRelativeDateException(Exception):
    pass


def _assume_clarification(base: datetime) -> DateClarification:
    pass


def get_day_time(day_time: DayTime, base: datetime = None) -> Tuple[int, int]:
    hour = day_time.hour
    minute = day_time.minute if day_time.minute else 0
    am_pm = day_time.am_pm

    UNK_TIME_OF_A_DAY = f"Unknown time of a day: {am_pm}"

    if day_time.hour > 12:
        return hour, minute

    elif day_time.hour == 12:
        if am_pm in (ToaD.NIGHT, ToaD.EVENING):
            return 0, minute

        elif am_pm in (ToaD.MORNING, ToaD.DAY):
            return 12, minute

        else:
            raise InvalidRelativeDateException(UNK_TIME_OF_A_DAY)

    else:
        if am_pm in (ToaD.MORNING, ToaD.NIGHT):
            return hour, minute
        elif am_pm in (ToaD.DAY, ToaD.EVENING):
            return hour + 12, minute
        else:
            raise InvalidRelativeDateException(UNK_TIME_OF_A_DAY)


def get_absolute_date(
        moment: Moment,
        base: datetime = None,
        clarification: DateClarification = None,
        assume_clarification=False
) -> datetime:
    if base is None:
        base = datetime.now()

    distance = moment.effective_date

    if isinstance(distance, RelativeInterval):
        unit = distance.unit

        simple_units = {
            TemporalUnit.HOUR: lambda: base + timedelta(hours=distance.amount if distance.amount else 1),
            TemporalUnit.MINUTE: lambda: base + timedelta(hours=distance.amount if distance.amount else 1),
            NamedInterval.HALF_AN_HOUR: lambda: base + timedelta(minutes=30),
        }

        if unit in simple_units:
            return simple_units[unit]()

        elif unit == TemporalUnit.DAY:
            return base + timedelta(days=distance.amount if distance.amount else 1)
        else:
            raise InvalidRelativeDateException(f"Unknown unit/amount combination: {unit}, {distance.amount}")

    if isinstance(distance, RelativeDay):
        pass

    else:
        raise InvalidRelativeDateException(f"This type of relative date is not supported: {type(distance).__name__}")
