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
    "час": 1,
    "два": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
    "десять": 10,
    "одинадцать": 11,
    "двенадцать": 12,
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
        gte(0),
        lte(24)
    )
)

DAY_OF_WEEK = dictionary(WORDS_DAY_OF_WEEK)

DAY_OF_WEEK_DISCRIMINATOR = dictionary(WORDS_DAY_OF_WEEK_DISCRIMINATOR)

AM_PM = dictionary(WORDS_AM_PM)


# Facts

class DayTime(FactDefinition):
    hour: Union[str, Attribute]
    minute: Union[str, Attribute]
    am_pm: Union[str, Attribute]


class RelativeDay(FactDefinition):
    relative_day: Union[str, Attribute]
    day_time: Union[DayTime, Attribute]


class DayOfWeek(FactDefinition):
    discriminator: Union[str, Attribute]
    day_of_week: Union[str, Attribute]
    day_time: Union[DayTime, Attribute]


class Moment(FactDefinition):
    effective_date: Union[RelativeDay, DayOfWeek, Attribute]


# RULES

RULE_DAY_TIME = rule(
    rule("в").optional(),

    HOUR_OF_A_DAY.interpretation(
        DayTime.hour.normalized().custom(lambda val: int(WORDS_HOUR_OF_A_DAY.get(val, val)))
    ),

    normalized("час").optional(),

    AM_PM.optional().interpretation(
        DayTime.am_pm.normalized()
    )
).interpretation(DayTime)

RULE_RELATIVE_DAY = rule(
    rule("в").optional(),

    RELATIVE_DAY.interpretation(
        RelativeDay.relative_day.normalized()
    ),

    RULE_DAY_TIME.optional().interpretation(
        RelativeDay.day_time
    )
).interpretation(RelativeDay)

RULE_DAY_OF_THE_WEEK = rule(
    rule("в").optional(),

    DAY_OF_WEEK_DISCRIMINATOR.optional().interpretation(
        DayOfWeek.discriminator.normalized()
    ),

    DAY_OF_WEEK.interpretation(
        DayOfWeek.day_of_week.normalized()
    ),

    RULE_DAY_TIME.optional().interpretation(
        DayOfWeek.day_time
    )
).interpretation(DayOfWeek)

RULE_MOMENT = or_(
    RULE_RELATIVE_DAY.interpretation(Moment.effective_date),

    RULE_DAY_OF_THE_WEEK.interpretation(Moment.effective_date),
).interpretation(Moment)

MOMENT_PARSER = Parser(RULE_MOMENT)


def analyse_natural_date(txt: str) -> Optional[Fact]:
    match = MOMENT_PARSER.find(txt)
    return match.fact if match else None
