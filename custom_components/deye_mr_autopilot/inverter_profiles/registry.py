"""Inverter profile registry."""

from .base import InverterProfile

_PROFILES: dict[tuple[str, str], InverterProfile] = {}


def get_profile(manufacturer: str, model: str) -> InverterProfile | None:
    """Return an exact model match; unknown profiles never permit writes."""
    return _PROFILES.get((manufacturer.casefold(), model.casefold()))
