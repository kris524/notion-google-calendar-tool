import unittest
from unittest.mock import patch, Mock
from notion_to_google_task_sync import get_all_pages

# simplified example result from client.search() used for mocking purposes
DUMMY_SEARCH_RES = {
    "has_more": False,
    "results": [
        {
            "archived": False,
            "cover": None,
            "created_time": "2023-09-16T15:09:00.000Z",
            "icon": None,
            "id": "1211a5ef-1425-40c7-abad-0cb6f98b6fcc",
            "last_edited_by": {
                "id": "9cb719ff-10ae-4f82-8677-c8c8232d665a",
                "object": "user",
            },
            "last_edited_time": "2023-10-28T14:28:00.000Z",
            "public_url": None,
        }
    ],
    "type": "page_or_database",
}


class TestNotionFunctions(unittest.TestCase):

    @patch("notion_to_google_task_sync.MockClient")
    def test_get_all_pages(self, mock_client):
        """Test correct ids are collected"""
        mock_search = Mock()
        mock_search.return_value = DUMMY_SEARCH_RES

        mock_client.search = mock_search

        actual = get_all_pages(mock_client)

        self.assertEqual(actual, [DUMMY_SEARCH_RES["results"][0]["id"]])
