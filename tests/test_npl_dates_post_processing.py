import unittest
from datetime import datetime, time

from typing import Tuple, NamedTuple

from parameterized import parameterized
from yargy import Parser

from tests.utils import escape_test_suffix
from tg_dobby.grammar.natural_dates_post_processing import (
    get_day_time,
    get_absolute_date,
    ALL_CLARIFICATIONS_CLASSES,
    DayTimeClarification,
    ClarificationRequired,
)
from tg_dobby.grammar.natural_dates import DayTime, RULE_DAY_TIME, Moment, RULE_MOMENT

CORRECT_TIME_CASES = (
    ("14:00", None, time(14, 00)),
    ("14:00:14", None, time(14, 00, 14)),
    ("02:00", None, time(2, 00)),
    ("два часа дня", None, time(14, 00)),
    ("два дня", None, time(14, 00)),
    ("12 ночи", None, time(00, 00)),
    ("12 утра", None, time(12, 00)),
    ("12 дня", None, time(12, 00)),
    ("3 утра", None, time(3, 00)),
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
        "через день",
        datetime(year=_Y, month=9, day=2, hour=23, minute=45),
        datetime(year=_Y, month=9, day=3, hour=23, minute=45),
    ),
    (
        "через неделю",
        datetime(year=_Y, month=9, day=2, hour=23, minute=45),
        datetime(year=_Y, month=9, day=9, hour=23, minute=45),
    ),
    (
        "завтра в 14:00",
        datetime(year=_Y, month=9, day=2, hour=13, minute=45),
        datetime(year=_Y, month=9, day=3, hour=14, minute=00),
    ),
    (
        "завтра в два дня",
        datetime(year=_Y, month=9, day=2, hour=13, minute=45),
        datetime(year=_Y, month=9, day=3, hour=14, minute=00),
    ),
    (
        "сегодня в 15:30",
        datetime(year=_Y, month=9, day=2, hour=13, minute=45),
        datetime(year=_Y, month=9, day=2, hour=15, minute=30),
    ),
    (
        "послезавтра в 15:30",
        datetime(year=_Y, month=12, day=31, hour=13, minute=45),
        datetime(year=_Y + 1, month=1, day=2, hour=15, minute=30),
    ),
)


class ClarifiedDateTimeCase(NamedTuple):
    text: str
    base_datetime: datetime
    clarification: ALL_CLARIFICATIONS_CLASSES
    expected_result: datetime


CLARIFICATION_DATE_TIME_CASES = (
    ClarifiedDateTimeCase(
        "завтра",
        datetime(year=_Y, month=9, day=2, hour=14, minute=45),
        DayTimeClarification(time(15, 00)),
        datetime(year=_Y, month=9, day=3, hour=15, minute=00),
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

    @parameterized.expand([
        (escape_test_suffix(case.text), case) for case in CLARIFICATION_DATE_TIME_CASES
    ])
    def test_clarified_moment(self, _, case: ClarifiedDateTimeCase):
        parsed_moment = self._parse_natural_daytime(case.text)

        # Check that clarification required fires
        with self.assertRaises(ClarificationRequired):
            get_absolute_date(parsed_moment, base=case.base_datetime)

        # Check that requested clarification matches expected type
        try:
            get_absolute_date(parsed_moment, base=case.base_datetime)
        except ClarificationRequired as e:
            self.assertListEqual(
                [type(case.clarification)],
                [type(rc) for rc in e.required_clarifications],
                "Requested clarification types does not match"
            )

        # Check with provided clarification
        actual_result = get_absolute_date(parsed_moment, base=case.base_datetime, clarifications=(case.clarification,))
        self.assertEqual(case.expected_result, actual_result, f"Wrong interpretation for {case.text}")


if __name__ == '__main__':
    unittest.main()
