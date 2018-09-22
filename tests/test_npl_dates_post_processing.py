import unittest
from datetime import datetime

from typing import Tuple

from parameterized import parameterized
from yargy import Parser

from tests.utils import escape_test_suffix
from tg_dobby.grammar.natural_dates_post_processing import get_day_time, get_absolute_date
from tg_dobby.grammar.natural_dates import DayTime, RULE_DAY_TIME, Moment, RULE_MOMENT

CORRECT_TIME_CASES = (
    ("14:00", (14, 00)),
    ("два часа дня", None, (14, 00)),
    ("два дня", None, (14, 00)),
    ("12 ночи", None, (00, 00)),
    ("12 утра", None, (12, 00)),
    ("12 дня", None, (12, 00)),
    ("3 утра", None, (3, 00)),
)


class TimeOfADayFullProcessingTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = Parser(RULE_DAY_TIME)

    def _parse_natural_daytime(self, txt) -> DayTime:
        m = self.parser.match(txt)

        self.assertIsNotNone(m, f"Phrase does not match day time pattern: {txt}")

        return m.fact

    @parameterized.expand([
        (escape_test_suffix(case[0]), *case) for case in CORRECT_TIME_CASES
    ])
    def test_correct_time(self, _, text, base_datetime: datetime, expected_time: Tuple[int, int]):
        parsed_day_time = self._parse_natural_daytime(text)

        actual_time = get_day_time(parsed_day_time, base=base_datetime)

        self.assertEqual(expected_time, actual_time, f"Wrong interpretation for {text}")


_Y = 2018

CORRECT_DATE_TIME_CASES = (
    (
        "через полчаса",
        datetime(year=_Y, month=9, day=2, hour=23, minute=45),
        datetime(year=_Y, month=9, day=3, hour=0, minute=15),
    ),
    (
        "через час",
        datetime(year=_Y, month=9, day=2, hour=23, minute=45),
        datetime(year=_Y, month=9, day=3, hour=0, minute=45),
    ),
    (
        "через 2 часа",
        datetime(year=_Y, month=9, day=2, hour=23, minute=45),
        datetime(year=_Y, month=9, day=3, hour=1, minute=45),
    ),
    (
        "завтра",
        datetime(year=_Y, month=9, day=2, hour=23, minute=45),
        datetime(year=_Y, month=9, day=3, hour=23, minute=45),
    ),
    (
        "через день",
        datetime(year=_Y, month=9, day=2, hour=23, minute=45),
        datetime(year=_Y, month=9, day=3, hour=23, minute=45),
    ),
    (
        "через неделю",
        datetime(year=_Y, month=9, day=2, hour=23, minute=45),
        datetime(year=_Y, month=9, day=9, hour=23, minute=45),
    ),
)


class NaturalDateFullProcessingTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = Parser(RULE_MOMENT)

    def _parse_natural_daytime(self, txt) -> Moment:
        m = self.parser.match(txt)

        self.assertIsNotNone(m, f"Phrase does not match moment pattern: {txt}")

        return m.fact

    @parameterized.expand([
        (escape_test_suffix(case[0]), *case) for case in CORRECT_DATE_TIME_CASES
    ])
    def test_correct_moment(self, _, text, base_datetime: datetime, expected_time: Tuple[int, int]):
        parsed_moment = self._parse_natural_daytime(text)

        actual_time = get_absolute_date(parsed_moment, base=base_datetime)

        self.assertEqual(expected_time, actual_time, f"Wrong interpretation for {text}")


if __name__ == '__main__':
    unittest.main()
