import unittest

from typing import Union, List

from parameterized import parameterized

from tests.utils import escape_test_suffix
from tg_dobby.grammar.natural_dates import Moment
from tg_dobby.grammar.tokenizer import tokenize_phrase, ReminderPreamble

CASES = (
    (
        "Напомни мне завтра в 3 дня позвонить маме",
        [
            ReminderPreamble,
            Moment,
            "позвонить маме",
        ]
    ),
    (
        "Напомни мне позвонить маме завтра в 3 дня послезавтра",
        [
            ReminderPreamble,
            "позвонить маме",
            Moment,
            Moment,
        ]
    ),
    (
        "напомни через полчаса позвонить маме",
        [
            ReminderPreamble,
            Moment,
            "позвонить маме",
        ]
    ),
    (
        "позвонить маме завтра",
        [
            "позвонить маме",
            Moment,
        ]
    ),
    (
        "позвонить маме через 10 минут",
        [
            "позвонить маме",
            Moment,
        ]
    ),
)


class PhraseTokenizerTestCase(unittest.TestCase):

    @parameterized.expand([
        (escape_test_suffix(case[0]), *case) for case in CASES
    ])
    def test_tokenize(self, _, text, expected_token_types_list: List[Union[str, type]]):
        token_list = tokenize_phrase(text)

        actual_token_list = [
            type(token.fact) if token.fact else token.text
            for token in token_list
        ]

        self.assertListEqual(actual_token_list, expected_token_types_list)


if __name__ == '__main__':
    unittest.main()
