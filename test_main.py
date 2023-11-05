import unittest
from unittest.mock import patch, Mock
from sync.notion_to_google_task_sync import get_all_pages, get_todo, get_all_blocks
import json
# simplified example result from client.search() used for mocking purposes


with open("test_assets/dummy_search_result.json", "r") as f:
    DUMMY_SEARCH_RES = json.load(f)

with open("test_assets/dummy_block_empty.json", "r") as f:

    DUMMY_BLOCK_EMPTY = json.load(f)

with open("test_assets/dummy_block_with_todo.json", "r") as f:

    DUMMY_WITH_TODO = json.load(f)


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
        """Test that get_all_blocks collects all the blocks of the given page id"""

        mock_search = Mock()
        mock_search.return_value = DUMMY_BLOCK_EMPTY
        mock_client.blocks.children.list = mock_search

        actual = get_all_blocks(mock_client, DUMMY_SEARCH_RES["results"][0]["id"])

        assert actual == DUMMY_BLOCK_EMPTY["results"]

    @patch("sync.notion_to_google_task_sync.Client")
    def test_get_todo_is_empty(self, mock_client):
        """Test that get_todo is empty given block with NO todos"""

        mock_search = Mock()
        mock_search.return_value = DUMMY_BLOCK_EMPTY
        mock_client.blocks.children.list = mock_search

        actual = get_todo(mock_client, DUMMY_BLOCK_EMPTY["results"])

        self.assertEqual(actual, [])

    @patch("sync.notion_to_google_task_sync.Client")
    def test_get_todo(self, mock_client):
        """Test that get_todo returns as expected given block WITH todos"""

        mock_search = Mock()
        mock_search.return_value = DUMMY_WITH_TODO
        mock_client.blocks.children.list = mock_search

        actual = get_todo(mock_client, DUMMY_WITH_TODO["results"])
        print(actual[0])
        expected = [{'status': 'completed', 'title': 'Hello World', 'id': '0f3d06aa-4a00-4ce8-81cd-02e9ea24efb1'}, {'status': 'completed', 'title': 'Cook Lunch', 'id': 'b05e6020-7df0-4d65-aa7c-47347dcfbf40'}]
        
        self.assertEqual(expected[0], actual[0])
        self.assertEqual(expected[1], actual[1])


    