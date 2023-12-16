"""Script that handles the sync from Google Tasks to Notion"""
from notion_client import Client
from typing import List
from sync.notion_to_google_task_sync import r_reverse, r


def get_pages_data(client: Client) -> List[str]:
    """Get all pages that have enabled the integration"""
    # import ipdb;ipdb.set_trace()
    pages_data = {}
    for page in client.search()["results"]:

        title = page["properties"]["title"]["title"][0]["plain_text"]
        pages_data[title] = page["id"]

    return pages_data


def insert_google_task_into_notion(service, client, notion_page_id, task_list_id):
    """Insert google tasks into notion"""

    current_google_tasks = [
        {"title": task["title"], "id": task["id"], "status": task["status"]}
        for task in service.tasks().list(tasklist=task_list_id).execute()["items"]
    ]

    for google_task in current_google_tasks[::-1]:
        if r_reverse.get(google_task["id"]) is None:

            if google_task["status"] == "needsAction":
                checked = False
            else:
                checked = True

            notion_task = client.blocks.children.append(
                notion_page_id,
                children=[
                    {
                        "to_do": {
                            "rich_text": [{"text": {"content": google_task["title"]}}],
                            "checked": checked,
                        }
                    }
                ],
            )

            # this should be done in another function. Use it for demo for now
            r.set(notion_task["results"][0]["id"], google_task["id"])
            r_reverse.set(google_task["id"], notion_task["results"][0]["id"])


def remove_deleted_google_tasks(service, client, task_list_id):
    """Delete NT that has been removed from GT"""

    current_google_task_ids = []

    current_google_task_ids = [
        task["id"]
        for task in service.tasks()
        .list(tasklist=task_list_id, showHidden=True)
        .execute()["items"]
    ]

    for google_task_id in r_reverse.keys():
        if google_task_id not in current_google_task_ids:

            notion_id_in_db = r_reverse.get(google_task_id)
            client.blocks.delete(notion_id_in_db)
            r.delete(notion_id_in_db)
            r_reverse.delete(google_task_id)


def update_notion_tasks(service, client, task_list_id):
    """Function that Updates tasks. Closes tasks marked as completed from Notion to Google Takss"""

    current_google_tasks = [
        {"title": task["title"], "id": task["id"], "status": task["status"]}
        for task in service.tasks()
        .list(tasklist=task_list_id, showHidden=True)
        .execute()["items"]
    ]

    for google_task in current_google_tasks:

        if r_reverse.get(google_task["id"]) is not None:
            block = client.blocks.retrieve(r_reverse.get(google_task["id"]))

            if google_task["status"] == "needsAction":
                block["to_do"]["checked"] = False
            else:
                block["to_do"]["checked"] = True

            block["to_do"]["rich_text"][0]["text"]["content"] = google_task["title"]
            block["to_do"]["rich_text"][0]["plain_text"] = google_task["title"]

            client.blocks.update(r_reverse.get(google_task["id"]), **block)
