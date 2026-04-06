# app/utils/date_utils.py

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


def resolve_date_range(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    preset: Optional[str] = None,
) -> Tuple[datetime, datetime]:
    """
    Resolves a valid date range for dashboard queries.
    Priority: preset > explicit dates > default (last 30 days)
    """

    now = datetime.now(timezone.utc)

    # -------- PRESETS --------
    if preset:
        if preset == "last_7_days":
            return now - timedelta(days=7), now

        elif preset == "last_30_days":
            return now - timedelta(days=30), now

        elif preset == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return start, now

        elif preset == "last_month":
            first_day_this_month = now.replace(day=1)
            last_month_end = first_day_this_month - timedelta(seconds=1)
            start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return start, last_month_end

        else:
            raise ValueError("Invalid preset")

    # -------- CUSTOM RANGE --------
    if from_date and to_date:
        if from_date > to_date:
            raise ValueError("from_date cannot be greater than to_date")

        return from_date, to_date

    # -------- DEFAULT --------
    return now - timedelta(days=30), now