from typing import Union, List, NamedTuple

import yargy
from yargy import rule, Parser, or_
from yargy.predicates import normalized

from tg_dobby.grammar.natural_dates import RULE_MOMENT
from tg_dobby.grammar.yargy_utils import FactDefinition


class RawText(NamedTuple):
    text: str


class ReminderPreamble(FactDefinition):
    target: str


RULE_REMINDER_PREAMBLE = rule(
    normalized("напомни"),
    normalized("мне").optional().interpretation(ReminderPreamble.target),
).interpretation(ReminderPreamble)


class TokenFact(FactDefinition):
    nested_fact: FactDefinition


def tokenize_phrase(txt: str, rules=(RULE_MOMENT, RULE_REMINDER_PREAMBLE,)) -> List[Union[RawText, yargy.parser.Match]]:
    parser = Parser(
        or_(*[
            r.interpretation(TokenFact.nested_fact) for r in rules
        ]).interpretation(TokenFact)
    )

    matches = parser.findall(txt)
    matches = sorted(matches, key=lambda m: m.span.start)

    expected_span_start = 0

    result = []

    for match in sorted(matches, key=lambda m: m.span.start):
        if match.span.start == expected_span_start:
            result.append(match)
        else:
            result.append(
                RawText(txt[expected_span_start:match.span.start].strip())
            )
            result.append(match)

        expected_span_start = match.span.stop + 1

    if expected_span_start < len(txt):
        tail = RawText(txt[expected_span_start:].strip())

        if tail:
            result.append(tail)

    return result


texts = [
    "Напомни мне завтра в 3 дня позвонить маме",
    "Напомни мне позвонить маме завтра в 3 дня послезавтра",
    "напомни через полчаса позвонить маме",
    "через полчаса позвонить маме",
    "позвонить маме завтра",
    "позвонить маме через 10 минут",
]


def _main():
    for p in texts:
        print()
        print("-" * 60)
        print(p)
        print("-" * 60)

        token_list = tokenize_phrase(p)
        for idx, token in enumerate(token_list):
            if isinstance(token, RawText):
                print("{}: '{}'".format(idx, token))
            else:
                print("{}: '{}'".format(idx, token.fact.nested_fact))


if __name__ == '__main__':
    _main()
