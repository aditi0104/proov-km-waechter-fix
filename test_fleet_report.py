# test_fleet_report.py
import fleet_utils
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
    fleet = [
        {"id": "VOS-0001", "odometer": 100, "last_service_km": 0},  # only 100 km - not due
        {"id": "VOS-7788", "odometer": 92000},                       # no last_service_km key
    ]
    result = fleet_summary(fleet)
    assert "average_wear" in result   # report completes without crashing
    assert result["due"] == 0         # neither car should be flagged
    assert result["no_reading"] == 1


def test_average_wear_ignores_cars_without_a_reading():
    fleet = [
        {"id": "A", "odometer": 14900, "last_service_km": 0},
        {"id": "B", "odometer": 3000, "last_service_km": 0},
        {"id": "C", "odometer": 92000},
    ]
    assert abs(fleet_summary(fleet)["average_wear"] - 59.67) < 0.01


def test_empty_fleet_does_not_divide_by_zero():
    assert fleet_summary([]) == {"count": 0, "due": 0, "no_reading": 0, "average_wear": 0.0}


def test_km_to_miles():
    assert abs(fleet_utils.km_to_miles(100) - 62.1371) < 1e-4
