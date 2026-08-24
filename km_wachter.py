# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return wear as a percentage of one service interval (can exceed 100)."""
    ratio = km_since_service / interval   # float division — keeps sub-interval fractions
    return ratio * 100


def needs_service(car: dict) -> bool:
    """Return True if the car has used >= WARN_AT_PERCENT of its service interval."""
    last = car.get("last_service_km")
    if last is None:
        return False                      # no reading → do not falsely flag
    km_since = car["odometer"] - last
    return wear_percent(km_since, SERVICE_INTERVAL_KM) >= WARN_AT_PERCENT


def check_fleet(fleet: list) -> list:
    """Print and return the IDs of every car that needs a service."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
