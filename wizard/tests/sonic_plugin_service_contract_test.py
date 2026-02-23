from __future__ import annotations

from wizard.services.sonic_plugin_service import SonicPluginService, get_sonic_service


def test_sonic_plugin_service_factory_returns_canonical_type() -> None:
    service = get_sonic_service()
    assert isinstance(service, SonicPluginService)
    assert isinstance(service.is_available(), bool)
