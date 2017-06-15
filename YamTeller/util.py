from math import floor
from decimal import Decimal
import settings
import re

r = re.compile(r"^Y?\d+(\.\d{2})?$")


def format_timedelta(value, time_format="{days} days, {hours2}:{minutes2}:{seconds2}"):
    if hasattr(value, 'seconds'):
        seconds = value.seconds + value.days * 24 * 3600
    else:
        seconds = int(value)

    seconds_total = seconds

    minutes = int(floor(seconds / 60))
    minutes_total = minutes
    seconds -= minutes * 60

    hours = int(floor(minutes / 60))
    hours_total = hours
    minutes -= hours * 60

    days = int(floor(hours / 24))
    days_total = days
    hours -= days * 24

    years = int(floor(days / 365))
    years_total = years
    days -= years * 365

    return time_format.format(**{
        'seconds': seconds,
        'seconds2': str(seconds).zfill(2),
        'minutes': minutes,
        'minutes2': str(minutes).zfill(2),
        'hours': hours,
        'hours2': str(hours).zfill(2),
        'days': days,
        'years': years,
        'seconds_total': seconds_total,
        'minutes_total': minutes_total,
        'hours_total': hours_total,
        'days_total': days_total,
        'years_total': years_total,
    })


def parse_amount(str_amount):
    if len(r.findall(str_amount)) != 1:
        raise ValueError(
            "Invalid amount. The amount needs to be a positive number at least equal to one cent. You can write it with or without a leading Y, with two or zero decimal places.")

    if str_amount.upper().startswith("Y"):
        str_amount = str_amount[1:]

    d = Decimal(str_amount)

    if d < settings.SMALLESTAMOUNT:
        raise ValueError("Invalid amount. The amount needs to be a positive number at least equal to one cent.")

    if d.remainder_near(settings.SMALLESTAMOUNT) != 0:
        raise ValueError("Invalid amount. The amount parameter should not contain sub-cent digits.")

    return d
