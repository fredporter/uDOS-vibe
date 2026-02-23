"""
Beacon Portal Test Plan

Comprehensive testing strategy for Beacon Portal implementation.
Covers unit tests, integration tests, performance tests, and security validation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import tempfile
from pathlib import Path

# ============================================================================
# UNIT TESTS: beacon_service.py
# ============================================================================


class TestBeaconConfig:
    """Test beacon configuration management."""

    def test_create_beacon_config(self):
        """Test creating a new beacon configuration."""
        from wizard.services.beacon_service import BeaconService, BeaconConfig, BeaconMode

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            config = BeaconConfig(
                beacon_id="beacon-test",
                mode=BeaconMode.PRIVATE_HOME,
                ssid="TestNetwork",
                band="both",
                security="wpa3",
                passphrase="knockknock",
                vpn_tunnel_enabled=True,
                cloud_enabled=False,
            )

            result = service.create_beacon_config(config)
            assert result.beacon_id == "beacon-test"
            assert result.mode == BeaconMode.PRIVATE_HOME

    def test_get_beacon_config(self):
        """Test retrieving beacon configuration."""
        from wizard.services.beacon_service import BeaconService, BeaconConfig, BeaconMode

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            config = BeaconConfig(
                beacon_id="beacon-test",
                mode=BeaconMode.PRIVATE_HOME,
                ssid="TestNetwork",
                band="both",
                security="wpa3",
                passphrase="knockknock",
                vpn_tunnel_enabled=True,
                cloud_enabled=False,
            )

            service.create_beacon_config(config)
            retrieved = service.get_beacon_config("beacon-test")

            assert retrieved is not None
            assert retrieved.beacon_id == "beacon-test"
            assert retrieved.ssid == "TestNetwork"

    def test_update_beacon_config(self):
        """Test updating beacon configuration."""
        from wizard.services.beacon_service import BeaconService, BeaconConfig, BeaconMode

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            config = BeaconConfig(
                beacon_id="beacon-test",
                mode=BeaconMode.PRIVATE_HOME,
                ssid="OldNetwork",
                band="2.4ghz",
                security="wpa2",
                passphrase="knockknock",
                vpn_tunnel_enabled=False,
                cloud_enabled=False,
            )

            service.create_beacon_config(config)
            service.update_beacon_config("beacon-test", {"ssid": "NewNetwork"})

            updated = service.get_beacon_config("beacon-test")
            assert updated.ssid == "NewNetwork"


class TestVPNTunnel:
    """Test VPN tunnel management."""

    def test_create_vpn_tunnel(self):
        """Test creating a new VPN tunnel."""
        from wizard.services.beacon_service import (
            BeaconService,
            VPNTunnel,
            TunnelStatus,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            tunnel = VPNTunnel(
                tunnel_id="tunnel-test",
                beacon_id="beacon-test",
                beacon_public_key="<public-key-1>",
                beacon_endpoint="203.0.113.1:51820",
                wizard_public_key="<public-key-2>",
            )

            result = service.create_vpn_tunnel(tunnel)
            assert result.tunnel_id == "tunnel-test"
            assert result.status == TunnelStatus.PENDING

    def test_update_tunnel_status(self):
        """Test updating tunnel status."""
        from wizard.services.beacon_service import (
            BeaconService,
            VPNTunnel,
            TunnelStatus,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            tunnel = VPNTunnel(
                tunnel_id="tunnel-test",
                beacon_id="beacon-test",
                beacon_public_key="<key1>",
                beacon_endpoint="203.0.113.1:51820",
                wizard_public_key="<key2>",
            )

            service.create_vpn_tunnel(tunnel)
            service.update_tunnel_status("tunnel-test", TunnelStatus.ACTIVE)

            updated = service.get_vpn_tunnel("tunnel-test")
            assert updated.status == TunnelStatus.ACTIVE

    def test_record_tunnel_stats(self):
        """Test recording tunnel statistics."""
        from wizard.services.beacon_service import (
            BeaconService,
            VPNTunnel,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            tunnel = VPNTunnel(
                tunnel_id="tunnel-test",
                beacon_id="beacon-test",
                beacon_public_key="<key1>",
                beacon_endpoint="203.0.113.1:51820",
                wizard_public_key="<key2>",
            )

            service.create_vpn_tunnel(tunnel)
            result = service.record_tunnel_stats(
                "tunnel-test",
                bytes_sent=1000000,
                bytes_received=5000000,
                latency_ms=45,
            )

            assert result is True


class TestDeviceQuota:
    """Test device quota management."""

    def test_create_device_quota(self):
        """Test creating device quota."""
        from wizard.services.beacon_service import (
            BeaconService,
            DeviceQuotaEntry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            quota = DeviceQuotaEntry(
                device_id="mobile-test",
                budget_monthly_usd=5.0,
            )

            result = service.create_device_quota(quota)
            assert result.device_id == "mobile-test"
            assert result.budget_monthly_usd == 5.0

    def test_deduct_quota(self):
        """Test deducting quota."""
        from wizard.services.beacon_service import (
            BeaconService,
            DeviceQuotaEntry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            quota = DeviceQuotaEntry(
                device_id="mobile-test",
                budget_monthly_usd=5.0,
            )

            service.create_device_quota(quota)
            service.deduct_quota("mobile-test", 1.0)

            updated = service.get_device_quota("mobile-test")
            assert updated.spent_this_month_usd == 1.0
            assert updated.requests_this_month == 1

    def test_quota_enforcement(self):
        """Test quota can't go over budget."""
        from wizard.services.beacon_service import (
            BeaconService,
            DeviceQuotaEntry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            quota = DeviceQuotaEntry(
                device_id="mobile-test",
                budget_monthly_usd=5.0,
            )

            service.create_device_quota(quota)

            # First deduction succeeds
            assert service.deduct_quota("mobile-test", 4.0) is True

            # Second deduction exceeds budget
            assert service.deduct_quota("mobile-test", 2.0) is False

            # Check final balance
            final = service.get_device_quota("mobile-test")
            assert final.spent_this_month_usd == 4.0

    def test_quota_reset(self):
        """Test monthly quota reset."""
        from wizard.services.beacon_service import (
            BeaconService,
            DeviceQuotaEntry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            quota = DeviceQuotaEntry(
                device_id="mobile-test",
                budget_monthly_usd=5.0,
            )

            service.create_device_quota(quota)
            service.deduct_quota("mobile-test", 3.0)

            # Verify spent
            before = service.get_device_quota("mobile-test")
            assert before.spent_this_month_usd == 3.0

            # Reset quota
            service.reset_device_quota("mobile-test")

            # Verify reset
            after = service.get_device_quota("mobile-test")
            assert after.spent_this_month_usd == 0.0
            assert after.requests_this_month == 0


class TestPluginCache:
    """Test plugin caching."""

    def test_cache_plugin(self):
        """Test caching a plugin."""
        from wizard.services.beacon_service import BeaconService

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            result = service.cache_plugin("my-plugin", "1.0.0", 2.5)
            assert result is True

            cached = service.get_cached_plugin("my-plugin")
            assert cached is not None
            assert cached["plugin_id"] == "my-plugin"
            assert cached["version"] == "1.0.0"

    def test_list_cached_plugins(self):
        """Test listing cached plugins."""
        from wizard.services.beacon_service import BeaconService

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            # Cache multiple plugins
            service.cache_plugin("plugin-1", "1.0.0", 1.0)
            service.cache_plugin("plugin-2", "2.0.0", 2.5)
            service.cache_plugin("plugin-3", "3.0.0", 3.0)

            # List plugins
            plugins = service.list_cached_plugins(limit=100)
            assert len(plugins) == 3


# ============================================================================
# INTEGRATION TESTS: beacon_routes.py
# ============================================================================


class TestBeaconRoutes:
    """Test Beacon Portal API routes."""

    @pytest.fixture
    def client(self):
        """Create test FastAPI client."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from wizard.routes.beacon_routes import create_beacon_routes

        app = FastAPI()
        app.include_router(create_beacon_routes(auth_guard=None))
        return TestClient(app)

    def test_configure_endpoint(self, client):
        """Test POST /api/beacon/configure"""
        response = client.post(
            "/api/beacon/configure",
            json={
                "mode": "private-home",
                "ssid": "TestNetwork",
                "band": "both",
                "security": "wpa3",
                "passphrase": "knockknock",
                "vpn_tunnel": False,
                "cloud_enabled": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["ssid"] == "TestNetwork"
        assert "beacon_id" in data

    def test_hardware_setup_endpoint(self, client):
        """Test POST /api/beacon/setup-hardware"""
        response = client.post(
            "/api/beacon/setup-hardware",
            json={"hardware": "tplink-wr841n"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "steps" in data
        assert len(data["steps"]) > 0

    def test_devices_list_endpoint(self, client):
        """Test GET /api/beacon/devices"""
        response = client.get("/api/beacon/devices")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_tunnel_enable_endpoint(self, client):
        """Test POST /api/beacon/tunnel/enable"""
        config_response = client.post(
            "/api/beacon/configure",
            json={
                "mode": "private-home",
                "ssid": "TestNetwork",
                "band": "both",
                "security": "wpa3",
                "passphrase": "knockknock",
                "vpn_tunnel": False,
                "cloud_enabled": False,
            },
        )
        assert config_response.status_code == 200
        beacon_id = config_response.json()["beacon_id"]

        response = client.post(
            "/api/beacon/tunnel/enable",
            json={
                "beacon_id": beacon_id,
                "beacon_public_key": "<key-1>",
                "beacon_endpoint": "203.0.113.1:51820",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["beacon_id"] == beacon_id
        assert data["status"] in {"pending", "active", "disabled"}
        assert "tunnel_id" in data
        assert "wizard_public_key" in data

    def test_quota_check_endpoint(self, client):
        """Test GET /api/beacon/devices/{device_id}/quota"""
        response = client.get("/api/beacon/devices/mobile-test/quota")

        assert response.status_code == 200
        data = response.json()
        assert "budget_monthly_usd" in data
        assert "remaining_usd" in data


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPerformance:
    """Performance and load testing."""

    def test_quota_check_latency(self):
        """Verify quota check is < 100ms."""
        from wizard.services.beacon_service import (
            BeaconService,
            DeviceQuotaEntry,
        )
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            quota = DeviceQuotaEntry(
                device_id="mobile-test",
                budget_monthly_usd=5.0,
            )
            service.create_device_quota(quota)

            start = time.time()
            for _ in range(100):
                service.get_device_quota("mobile-test")
            elapsed = time.time() - start

            avg_latency = (elapsed / 100) * 1000  # ms
            assert avg_latency < 100, f"Quota check latency: {avg_latency:.2f}ms"

    def test_beacon_config_creation_latency(self):
        """Verify beacon config creation is < 500ms."""
        from wizard.services.beacon_service import (
            BeaconService,
            BeaconConfig,
            BeaconMode,
        )
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            start = time.time()
            for i in range(10):
                config = BeaconConfig(
                    beacon_id=f"beacon-{i}",
                    mode=BeaconMode.PRIVATE_HOME,
                    ssid=f"Network{i}",
                    band="both",
                    security="wpa3",
                    passphrase="knockknock",
                    vpn_tunnel_enabled=False,
                    cloud_enabled=False,
                )
                service.create_beacon_config(config)
            elapsed = time.time() - start

            avg_latency = (elapsed / 10) * 1000  # ms
            assert avg_latency < 500, f"Config creation latency: {avg_latency:.2f}ms"


# ============================================================================
# SECURITY TESTS
# ============================================================================


class TestSecurity:
    """Security validation tests."""

    def test_quota_prevents_overspend(self):
        """Verify quota enforcement prevents overspending."""
        from wizard.services.beacon_service import (
            BeaconService,
            DeviceQuotaEntry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            quota = DeviceQuotaEntry(
                device_id="mobile-test",
                budget_monthly_usd=5.0,
            )
            service.create_device_quota(quota)

            # Try to spend more than budget
            result = service.deduct_quota("mobile-test", 10.0)
            assert result is False

    def test_device_quota_isolation(self):
        """Verify quotas are isolated per device."""
        from wizard.services.beacon_service import (
            BeaconService,
            DeviceQuotaEntry,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            service = BeaconService(db_path)

            # Create two devices
            quota1 = DeviceQuotaEntry(
                device_id="device-1",
                budget_monthly_usd=5.0,
            )
            quota2 = DeviceQuotaEntry(
                device_id="device-2",
                budget_monthly_usd=10.0,
            )

            service.create_device_quota(quota1)
            service.create_device_quota(quota2)

            # Deduct from device-1
            service.deduct_quota("device-1", 3.0)

            # Verify device-2 is not affected
            q1 = service.get_device_quota("device-1")
            q2 = service.get_device_quota("device-2")

            assert q1.spent_this_month_usd == 3.0
            assert q2.spent_this_month_usd == 0.0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
