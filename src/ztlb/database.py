"""Database operations for ZTL zones."""

import json
from pathlib import Path
from typing import Any

# Path to zones data
ZONES_FILE = Path(__file__).parent / 'storage' / 'zones.json'


def load_zones() -> dict[str, Any] | Any:
    """Load ZTL zones from JSON file.

    Returns:
        Dict containing zone data keyed by zone ID.

    Raises:
        FileNotFoundError: If zones.json doesn't exist.
        json.JSONDecodeError: If JSON is malformed.
    """
    with ZONES_FILE.open('r', encoding='utf-8') as f:
        return json.load(f)


def get_zone_by_id(zone_id: str) -> dict[str, Any] | None:
    """Get a specific ZTL zone by ID.

    Args:
        zone_id: The zone identifier.

    Returns:
        Zone data dict or None if not found.
    """
    zones = load_zones()
    return zones.get(zone_id)


def get_all_zones() -> list[dict[str, Any]]:
    """Get all ZTL zones as a list.

    Returns:
        List of zone data dicts with 'id' field added.
    """
    zones = load_zones()
    zone_list = []

    for zone_id, zone_data in zones.items():
        zone_with_id = {'id': zone_id, **zone_data}
        zone_list.append(zone_with_id)

    return zone_list


def get_zones_by_city(city: str = 'milano') -> list[dict[str, Any]]:
    """Get all zones for a specific city.

    Args:
        city: City name (currently only 'milano' supported).

    Returns:
        List of zone data dicts for the city.
    """
    # For MVP, we only have Milano data
    if city.lower() == 'milano':
        return get_all_zones()
    return []
