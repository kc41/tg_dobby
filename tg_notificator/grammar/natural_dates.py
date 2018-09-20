from typing import Optional, Union
from yargy import Parser, rule, and_, or_
from yargy.interpretation.attribute import Attribute
from yargy.interpretation.fact import Fact
from yargy.predicates import dictionary, gte, lte, normalized

# WORDS
from tg_notificator.grammar.yargy_utils import FactDefinition

WORDS_RELATIVE_DAY = {
    "сегодня",
    "завтра",
    "послезавтра",
}

WORDS_DAY_OF_WEEK = {
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
}

WORDS_HOUR_OF_A_DAY = {
    "час": "1",
    "два": "2",
    "три": "3",
    "четыре": "4",
    "пять": "5",
    "шесть": "6",
    "семь": "7",
    "восемь": "8",
    "девять": "9",
    "десять": "10",
    "одинадцать": "11",
    "двенадцать": "12",
}

WORDS_AM_PM = {
    "день",
    "ночь",
    "утро",
    "вечер",
}

WORDS_DAY_OF_WEEK_DISCRIMINATOR = {
    "эта",
    "следующая",
    "ближайшая",
}

# Parts

RELATIVE_DAY = dictionary(WORDS_RELATIVE_DAY)

HOUR_OF_A_DAY = or_(
    dictionary(WORDS_HOUR_OF_A_DAY),
    and_(
        gte(1),
        lte(23)
    )
)

DAY_OF_WEEK = dictionary(WORDS_DAY_OF_WEEK)

DAY_OF_WEEK_DISCRIMINATOR = dictionary(WORDS_DAY_OF_WEEK_DISCRIMINATOR)

AM_PM = dictionary(WORDS_AM_PM)


# Facts

class RelativeDayTimeFact(FactDefinition):
    relative_day: Union[str, Attribute]
    hour: Union[str, Attribute]
    am_pm: Union[str, Attribute]


class DayOfWeekTimeFact(FactDefinition):
    discriminator: Union[str, Attribute]
    day_of_week: Union[str, Attribute]
    hour: Union[str, Attribute]
    am_pm: Union[str, Attribute]


# RULES

RULE_DAY_OF_WEEK_TIME = rule(
    rule("в").optional(),
    DAY_OF_WEEK_DISCRIMINATOR.optional().interpretation(
        DayOfWeekTimeFact.discriminator
    ),
    DAY_OF_WEEK.interpretation(
        DayOfWeekTimeFact.day_of_week.normalized()
    ),
    rule(
        rule("в").optional(),
        HOUR_OF_A_DAY.interpretation(
            DayOfWeekTimeFact.hour
        ),

        normalized("час").optional(),

        AM_PM.optional().interpretation(
            DayOfWeekTimeFact.am_pm.normalized()
        )
    ).optional()
).interpretation(
    DayOfWeekTimeFact
)

RULE_RELATIVE_DAY_TIME = rule(
    RELATIVE_DAY.interpretation(
        RelativeDayTimeFact.relative_day
    ),
    rule(
        rule("в").optional(),

        HOUR_OF_A_DAY.interpretation(
            RelativeDayTimeFact.hour
        ),

        normalized("час").optional(),

        AM_PM.optional().interpretation(
            RelativeDayTimeFact.am_pm.normalized()
        )
    ).optional()
).interpretation(
    RelativeDayTimeFact
)

text = """
завтра в полдень
завтра
Послезавтра в 4 часа дня
Послезавтра в 4 дня
Через неделю
Завтра в 4
В эту пятницу в 4
В понедельник
В эту пятницу
21 числа
"""

PARSER_DAY_OF_WEEK = Parser(RULE_DAY_OF_WEEK_TIME)

PARSER_RELATIVE_DAY = Parser(RULE_RELATIVE_DAY_TIME)


def analyse_natural_date(txt: str) -> Optional[Fact]:
    parsers = (PARSER_DAY_OF_WEEK, PARSER_RELATIVE_DAY)

    for parser in parsers:
        match = parser.find(txt)

        if match:
            return match.fact

    return None


if __name__ == '__main__':
    for line in text.split("\n"):
        if not line:
            continue

        f = analyse_natural_date(line)
        print(f"{line:<30} -> {f.as_json if f else ''}")
