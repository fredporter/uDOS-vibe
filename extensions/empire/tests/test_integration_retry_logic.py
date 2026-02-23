import unittest
from unittest.mock import MagicMock, patch

from empire.integrations import hubspot, google_places


class IntegrationRetryTests(unittest.TestCase):
    def test_hubspot_request_with_retry_recovers_after_failure(self):
        ok_response = MagicMock()
        ok_response.raise_for_status.return_value = None

        with patch('empire.integrations.hubspot.requests.get') as mock_get, patch('empire.integrations.hubspot.time.sleep'):
            mock_get.side_effect = [Exception('temporary'), ok_response]
            resp = hubspot._request_with_retry('https://example.test', {}, token='x', retries=2)

        self.assertIs(resp, ok_response)
        self.assertEqual(mock_get.call_count, 2)

    def test_places_request_with_retry_raises_after_exhaustion(self):
        with patch('empire.integrations.google_places.requests.get', side_effect=Exception('boom')), patch(
            'empire.integrations.google_places.time.sleep'
        ):
            with self.assertRaises(Exception):
                google_places._request_with_retry('https://example.test', {}, retries=2)


if __name__ == '__main__':
    unittest.main()
