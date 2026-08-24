# test_fleet_report.py
from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_does_not_crash_on_missing_reading():
    # A car with no last_service_km (like VOS-7788) must not raise KeyError.
    # Use a fresh-off-the-lot car (0 km) so it is definitely not due, plus the no-reading car.
    fleet = [
        {"id": "VOS-0001", "odometer": 100, "last_service_km": 0},  # only 100 km — not due
        {"id": "VOS-7788", "odometer": 92000},                       # no last_service_km key
    ]
    result = fleet_summary(fleet)
    assert "average_wear" in result   # report completes without crashing
    assert result["due"] == 0         # neither car should be flagged
