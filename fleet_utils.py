# fleet_utils.py
# Shared helpers for the KM-Waechter fleet service.

KM_TO_MILES = 0.621371


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * KM_TO_MILES


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"
