import unittest

from typing import Union

from parameterized import parameterized

from tests.utils import escape_test_suffix
from tg_dobby.grammar import extract_first_natural_date
from tg_dobby.grammar.model import TemporalUnit, NamedInterval, RelativeDayOption, UnitRelativePosition, TimesOfADayOption
from tg_dobby.grammar.natural_dates import Moment, DayOfWeek, DayTime, RelativeDay, RelativeInterval

CASES = (
    (
        "завтра",
        RelativeDay(
            relative_day=RelativeDayOption.TOMORROW,
            day_time=None
        )
    ),
    (
        "Послезавтра в 4 часа дня",
        RelativeDay(
            relative_day=RelativeDayOption.THE_DAY_AFTER_TOMORROW,
            day_time=DayTime(
                hour=4,
                am_pm=TimesOfADayOption.DAY,
            )
        )
    ),
    (
        "Послезавтра в четыре часа дня",
        RelativeDay(
            relative_day=RelativeDayOption.THE_DAY_AFTER_TOMORROW,
            day_time=DayTime(
                hour=4,
                am_pm=TimesOfADayOption.DAY,
            )
        )
    ),
    (
        "Послезавтра в две часа дня",
        RelativeDay(
            relative_day=RelativeDayOption.THE_DAY_AFTER_TOMORROW,
            day_time=DayTime(
                hour=2,
                am_pm=TimesOfADayOption.DAY,
            )
        )
    ),
    (
        "Послезавтра в 4 дня",
        RelativeDay(
            relative_day=RelativeDayOption.THE_DAY_AFTER_TOMORROW,
            day_time=DayTime(
                hour=4,
                am_pm=TimesOfADayOption.DAY,
            )
        )
    ),
    (
        "Завтра в 4",
        RelativeDay(
            relative_day=RelativeDayOption.TOMORROW,
            day_time=DayTime(
                hour=4,
            )
        )
    ),
    (
        "В эту пятницу в 4",
        DayOfWeek(
            discriminator=UnitRelativePosition.THIS,
            day_of_week="пятница",
            day_time=DayTime(
                hour=4,
                minute=None,
                am_pm=None
            )
        )
    ),
    (
        "В понедельник",
        DayOfWeek(
            discriminator=None,
            day_of_week="понедельник",
            day_time=None
        )
    ),
    (
        "В эту пятницу",
        DayOfWeek(
            discriminator=UnitRelativePosition.THIS,
            day_of_week="пятница",
            day_time=None
        )
    ),
    # Через X
    (
        "Через 30 минут",
        RelativeInterval(
            unit=TemporalUnit.MINUTE,
            amount=30,
        )
    ),
    (
        "Через полчаса",
        RelativeInterval(
            unit=NamedInterval.HALF_AN_HOUR,
            amount=None,
        )
    ),
    (
        "Через месяц",
        RelativeInterval(
            unit=TemporalUnit.MONTH,
            amount=None,
        )
    ),
    (
        "Через 1 месяц",
        RelativeInterval(
            unit=TemporalUnit.MONTH,
            amount=1,
        )
    ),
)


class NaturalDatesTestCase(unittest.TestCase):

    @parameterized.expand([
        (escape_test_suffix(case[0]), *case) for case in CASES
    ])
    def test_parse(self, _, text, expected: Union[DayOfWeek, RelativeDay]):
        actual_moment = extract_first_natural_date(text)

        expected_moment = Moment(
            effective_date=expected
        ) if expected else None

        self.assertEqual(expected_moment, actual_moment)


if __name__ == '__main__':
    unittest.main()
