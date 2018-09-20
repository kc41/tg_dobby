import unittest

import re
from typing import Union

from parameterized import parameterized
from transliterate import translit

from tg_notificator.grammar import analyse_natural_date
from tg_notificator.grammar.natural_dates import Moment, DayOfWeek, DayTime, RelativeDay

CASES = (
    (
        "завтра",
        RelativeDay(
            relative_day="завтра",
            day_time=None
        )
    ),
    (
        "Послезавтра в 4 часа дня",
        RelativeDay(
            relative_day="послезавтра",
            day_time=DayTime(
                hour="4",
                am_pm="день",
            )
        )
    ),
    (
        "Послезавтра в четыре часа дня",
        RelativeDay(
            relative_day="послезавтра",
            day_time=DayTime(
                hour="4",
                am_pm="день",
            )
        )
    ),
    (
        "Послезавтра в 4 дня",
        RelativeDay(
            relative_day="послезавтра",
            day_time=DayTime(
                hour="4",
                am_pm="день",
            )
        )
    ),
    (
        "Завтра в 4",
        RelativeDay(
            relative_day="завтра",
            day_time=DayTime(
                hour="4",
            )
        )
    ),
    (
        "В эту пятницу в 4",
        DayOfWeek(
            discriminator="этот",
            day_of_week="пятница",
            day_time=DayTime(
                hour="4",
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
            discriminator="этот",
            day_of_week="пятница",
            day_time=None
        )
    ),
)


def escape_test_suffix(txt):
    return re.sub(r"[\s\-]+", "_", translit(txt.lower(), reversed=True))


class NaturalDatesTestCase(unittest.TestCase):

    def test_test(self):
        pass

    @parameterized.expand([
        (escape_test_suffix(case[0]), *case) for case in CASES
    ])
    def test_parse(self, _, text, expected: Union[DayOfWeek, RelativeDay]):
        actual_moment = analyse_natural_date(text)

        expected_moment = Moment(
            effective_date=expected
        ) if expected else None

        self.assertEqual(actual_moment, expected_moment)


if __name__ == '__main__':
    unittest.main()
