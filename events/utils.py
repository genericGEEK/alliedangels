import calendar
from datetime import date

def nth_weekday_of_month(year, month, weekday, n):
    """
    weekday: 0=Mon ... 6=Sun
    n: 1=first, 2=second, 3=third, 4=fourth, 5=last
    """
    cal = calendar.Calendar()
    days = [
        d for d in cal.itermonthdates(year, month)
        if d.month == month and d.weekday() == weekday
    ]

    if not days:
        return None

    if n == 5:
        return days[-1]

    return days[n - 1] if len(days) >= n else None
