import unittest
from unittest.mock import patch, Mock
from sync.notion_to_google_task_sync import get_all_pages, get_todo, get_all_blocks

# simplified example result from client.search() used for mocking purposes

# put those mock assests in json
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

DUMMY_BLOCK = {
    "object": "list",
    "results": [
        {
            "object": "block",
            "id": "57ad65c5-bc03-42f5-ae1d-5a37c1ed7806",
            "parent": {
                "type": "page_id",
                "page_id": "1211a5ef-1425-40c7-abad-0cb6f98b6fcc",
            },
            "created_time": "2023-09-17T15:15:00.000Z",
            "last_edited_time": "2023-09-17T15:15:00.000Z",
            "created_by": {
                "object": "user",
                "id": "9cb719ff-10ae-4f82-8677-c8c8232d665a",
            },
            "last_edited_by": {
                "object": "user",
                "id": "9cb719ff-10ae-4f82-8677-c8c8232d665a",
            },
            "has_children": False,
            "archived": False,
            "type": "heading_2",
        }
    ],
    "next_cursor": None,
    "has_more": False,
    "type": "block",
    "block": {},
    "request_id": "1846764f-0811-4c76-83d5-4d4476c9d8e1",
}

class TestNotionFunctions(unittest.TestCase):
    @patch("sync.notion_to_google_task_sync.Client")
    def test_get_all_pages(self, mock_client):
        """Test correct ids are collected"""
        mock_search = Mock()
        mock_search.return_value = DUMMY_SEARCH_RES
        mock_client.search = mock_search

        actual = get_all_pages(mock_client)

        self.assertEqual(actual, [DUMMY_SEARCH_RES["results"][0]["id"]])

    @patch("sync.notion_to_google_task_sync.Client")
    def test_get_all_blocks(self, mock_client):
        """Test correct ids are collected"""

        mock_search = Mock()
        mock_search.return_value = DUMMY_BLOCK
        mock_client.blocks.children.list = mock_search

        actual = get_all_blocks(mock_client, DUMMY_SEARCH_RES["results"][0]["id"])

        assert actual == DUMMY_BLOCK["results"]
