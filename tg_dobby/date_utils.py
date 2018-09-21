import calendar
import datetime


def add_months(source_date: datetime.datetime, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1

    day = min(source_date.day, calendar.monthrange(year, month)[1])

    return source_date.replace(
        year=year,
        month=month,
        day=day,
    )
