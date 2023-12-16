import os
from notion_client import Client
from pprint import pprint
from dotenv import load_dotenv
from typing import List, Dict
import os.path
import logging

from sync.notion_to_google_task_sync import (
    authenticate_and_print,
    get_all_pages,
    get_all_blocks,
    get_todo,
    create_notion_tasklist,
    insert_notion_tasks_in_google_tasks,
    add_id_mapping_to_redis,
    update_google_tasks,
    remove_deleted_tasks_ids_from_redis,
)

from sync.google_to_notion_task_sync import (
    update_notion_tasks,
    remove_deleted_google_tasks,
    insert_google_task_into_notion,
)

if __name__ == "__main__":

    load_dotenv()
    NOTION_ID = os.getenv("NOTION_KEY")
    if NOTION_ID is None:
        raise KeyError("Missing NOTION ID environment variable")

    service = authenticate_and_print()

    # Create Client
    client = Client(auth=NOTION_ID)

    # Get all page ids
    page_ids = get_all_pages(client)

    # Get every block from each page id
    total_blocks = []

    for page_id in page_ids:
        total_blocks.extend(get_all_blocks(client, page_id))

    # Get all Notion todos
    total_notion_tasks = get_todo(client, total_blocks)


    for page_id in page_ids:
        all_blocks = []

        all_blocks.extend(get_all_blocks(client, page_id))
        notion_tasks = get_todo(client, all_blocks)

        title = client.blocks.retrieve(page_id)["child_page"]["title"]
        TASK_LIST_ID = create_notion_tasklist(service, title)

        # Insert tasks from Notion to Google
        insert_notion_tasks_in_google_tasks(service, notion_tasks, TASK_LIST_ID)
        add_id_mapping_to_redis(service, notion_tasks, TASK_LIST_ID)
        remove_deleted_tasks_ids_from_redis(service, total_notion_tasks, TASK_LIST_ID)
        update_google_tasks(service, notion_tasks, TASK_LIST_ID)

