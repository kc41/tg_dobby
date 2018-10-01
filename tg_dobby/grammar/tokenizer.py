from typing import Union, List, NamedTuple, Optional

import yargy
from yargy import rule, Parser, or_
from yargy.predicates import normalized

from tg_dobby.grammar.natural_dates import RULE_MOMENT
from tg_dobby.grammar.yargy_utils import FactDefinition


class ReminderPreamble(FactDefinition):
    target: str


RULE_REMINDER_PREAMBLE = rule(
    normalized("напомни"),
    normalized("мне").optional().interpretation(ReminderPreamble.target),
).interpretation(ReminderPreamble)


class TokenFact(FactDefinition):
    nested_fact: FactDefinition


class PhraseToken:

    def __init__(self, text, match=None):
        self._match = match  # type: yargy.parser.Match
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    @property
    def fact(self) -> Optional[FactDefinition]:
        if self._match and self._match.fact and hasattr(self._match.fact, 'nested_fact'):
            return self._match.fact.nested_fact

        return None

    def __repr__(self):
        return f"{self.text} > {self.fact}"


def tokenize_phrase(txt: str, rules=(RULE_MOMENT, RULE_REMINDER_PREAMBLE,)) -> List[PhraseToken]:
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
            result.append(PhraseToken(
                txt[match.span.start:match.span.stop], match=match
            ))
        else:
            result.append(
                PhraseToken(txt[expected_span_start:match.span.start].strip())
            )
            result.append(PhraseToken(
                txt[match.span.start:match.span.stop], match=match
            ))

        expected_span_start = match.span.stop + 1

    if expected_span_start < len(txt):
        tail_text = txt[expected_span_start:].strip()

        if tail_text:
            result.append(PhraseToken(tail_text))

    return result
