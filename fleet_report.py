# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.

import json
import sys
from pathlib import Path

import fleet_utils
from config_loader import get_setting, load_settings
from km_wachter import car_wear_percent, needs_service
from log_util import flush_log, log


def fleet_summary(fleet: list) -> dict:
    """Return fleet size, cars due, cars without a usable reading and average wear.

    Average wear covers only cars with a usable reading; an empty fleet or a
    fleet with no readings averages 0.0.
    """
    wears = [w for w in map(car_wear_percent, fleet) if w is not None]
    return {
        "count": len(fleet),
        "due": sum(needs_service(car) for car in fleet),
        "no_reading": len(fleet) - len(wears),
        "average_wear": sum(wears) / len(wears) if wears else 0.0,
    }


def print_report(fleet: list) -> None:
    """Print the nightly fleet-health report and append it to the log file."""
    settings = load_settings()
    try:
        log(get_setting(settings, "report_title", "Nightly fleet report"))
        s = fleet_summary(fleet)
        print(f"Fleet: {s['count']} cars")
        print(f"Due for service: {s['due']}")
        print(f"No usable service reading: {s['no_reading']}")
        print(f"Average wear: {s['average_wear']:.1f}%")
        total_km = sum(car.get("odometer", 0) for car in fleet)
        # The partner garage in England wants the distance in miles (since 2015).
        print(f"Fleet distance: {fleet_utils.format_number(fleet_utils.km_to_miles(total_km))} miles")
    finally:
        flush_log(get_setting(settings, "log_file", "km_wachter.log"))


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("fleet_sample.json")
    print_report(json.loads(path.read_text(encoding="utf-8")))
