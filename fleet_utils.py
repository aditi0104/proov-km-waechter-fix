# fleet_utils.py
# Shared helpers for the KM-Waechter fleet service.
# Dead functions (is_due, parse_service_date, chunk_list) removed — none were called.

KM_TO_MILES = 0.621371                  # corrected: was 1.609 (km-per-mile), not miles-per-km


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * KM_TO_MILES


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list; 0 if the list is empty."""
    total = 0.0
    count = 0
    for v in values:
        total += v
        count += 1
    if count == 0:
        return 0.0
    return total / count
