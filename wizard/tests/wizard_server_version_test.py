from wizard import server


def test_get_wizard_server_version_matches_manifest() -> None:
    version = server.get_wizard_server_version()
    assert version == "1.1.3"
    assert server.WIZARD_SERVER_VERSION == version
