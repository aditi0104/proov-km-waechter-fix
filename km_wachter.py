# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.

from config_loader import get_int, load_settings

# settings.cfg is the single source of truth for the two rule values;
# the fallbacks are the approved values (15000 km, 80 %).
_settings = load_settings()
SERVICE_INTERVAL_KM = get_int(_settings, "service_interval_km", 15000)
WARN_AT_PERCENT = get_int(_settings, "warn_at_percent", 80)


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return wear as a percentage of one service interval (can exceed 100)."""
    return km_since_service / interval * 100


def car_wear_percent(car: dict) -> float | None:
    """Return the car's wear %, or None if the readings are missing or inconsistent."""
    last = car.get("last_service_km")
    odometer = car.get("odometer")
    if last is None or odometer is None or odometer < last:
        return None
    return wear_percent(odometer - last, SERVICE_INTERVAL_KM)


def needs_service(car: dict) -> bool:
    """Return True if the car has used >= WARN_AT_PERCENT of its service interval.

    A car without a usable reading is never flagged (fleet_report surfaces
    those cars separately instead).
    """
    wear = car_wear_percent(car)
    return wear is not None and wear >= WARN_AT_PERCENT


def check_fleet(fleet: list) -> list:
    """Print and return the IDs of every car that needs a service."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
