import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from empire.integrations import hubspot, google_places


class IntegrationSyncContractTests(unittest.TestCase):
    def test_hubspot_sync_contacts_accepts_sparse_properties(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / 'empire.db'
            sample = [{"id": "1", "properties": {"firstname": "Ada", "lastname": "Lovelace"}}]
            with patch('empire.integrations.hubspot.fetch_contacts', return_value=sample):
                count = hubspot.sync_contacts(token='dummy', db_path=db_path, limit=1, max_pages=1)

            self.assertEqual(count, 1)

    def test_places_ingest_uses_details_fallback(self):
        class MockPlacesClient:
            def __init__(self, *, api_key: str):
                self.api_key = api_key

            def search(self, query: str, location: str = '', radius_meters: int = 5000):
                return [{"place_id": "p1", "name": "Seed Name", "formatted_address": "A"}]

            def details(self, place_id: str):
                return {"name": "Detail Name", "formatted_address": "B", "international_phone_number": "+1-555-0001"}

        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / 'empire.db'
            with patch('empire.integrations.google_places.GooglePlacesClient', MockPlacesClient):
                count = google_places.search_and_ingest(api_key='dummy', query='qa', db_path=db_path)
            self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()
