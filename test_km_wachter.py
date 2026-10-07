# test_km_wachter.py
import km_wachter
from km_wachter import car_wear_percent, needs_service, wear_percent


def test_almost_due_car_is_flagged():
    # A car at 14,900 of its 15,000 km window is about 99% worn and MUST be flagged.
    assert needs_service({"id": "VOS-4471", "odometer": 14900, "last_service_km": 0}) is True


def test_missing_reading_is_not_treated_as_zero():
    # A car with NO last-service reading must not be treated as fully worn.
    assert needs_service({"id": "VOS-7788", "odometer": 92000}) is False


def test_rules_match_the_approved_values():
    assert km_wachter.SERVICE_INTERVAL_KM == 15000
    assert km_wachter.WARN_AT_PERCENT == 80


def test_threshold_is_inclusive_at_80_percent():
    assert needs_service({"id": "a", "odometer": 12000, "last_service_km": 0}) is True
    assert needs_service({"id": "b", "odometer": 11999, "last_service_km": 0}) is False


def test_wear_keeps_fractions():
    assert abs(wear_percent(14900, 15000) - 99.33) < 0.01


def test_odometer_below_last_service_is_unusable_not_negative_wear():
    car = {"id": "x", "odometer": 100, "last_service_km": 500}
    assert car_wear_percent(car) is None
    assert needs_service(car) is False


def test_missing_odometer_does_not_crash():
    assert needs_service({"id": "x", "last_service_km": 0}) is False
