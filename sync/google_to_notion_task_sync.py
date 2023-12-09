"""Script that handles the sync from Google Tasks to Notion"""
import os
from notion_client import Client
from dotenv import load_dotenv
import os.path
from typing import List
from notion_to_google_task_sync import authenticate_and_print
from notion_to_google_task_sync import r_reverse, r


def get_pages_data(client: Client) -> List[str]:
    """Get all pages that have enabled the integration"""
    # import ipdb;ipdb.set_trace()
    pages_data = {}
    for page in client.search()["results"]:

        title = page["properties"]["title"]["title"][0]["plain_text"]
        pages_data[title] = page["id"]

    return pages_data


# DONE: Also, update the redis db to have the reverse mapping, map from G id to N id
# DONE If a task is ticked on Google Calendar, it should be ticket on Notion as well, etc.
# DONE If a task is changed (text edited) in GC it should be changed in Notion as well
# DONE If a task is added in GC, add it to Notion, corresponding page AND redis
# DONE If a task is deleted on GC, if should be deleted in Notion as well AND in the database


def insert_google_task_into_notion(service, client, task_list_id):
    """Insert google tasks into notion"""

    current_google_tasks = [
        {"title": task["title"], "id": task["id"], "status": task["status"]}
        for task in service.tasks().list(tasklist=task_list_id).execute()["items"]
    ]

    # get the notion page id of the page where we want to insert the new task
    google_tasklist_title = (
        service.tasklists().get(tasklist=task_list_id).execute()["title"]
    )
    pages_data = get_pages_data(client)
    notion_page_id = pages_data[google_tasklist_title]

    for google_task in current_google_tasks[::-1]:
        # if we reach an id that
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


def remove_deleted_google_tasks(service, client, task_list_ids):
    """Delete NT that has been removed from GT"""

    current_google_task_ids = []

    for tasklist_id in task_list_ids:  # get all tasks from each Google tasklist

        current_google_task_ids.extend(
            [
                task["id"]
                for task in service.tasks()
                .list(tasklist=tasklist_id, showHidden=True)
                .execute()["items"]
            ]
        )

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


if __name__ == "__main__":
    load_dotenv()
    NOTION_ID = os.getenv("NOTION_KEY")

    client = Client(auth=NOTION_ID)
    service = authenticate_and_print()

    update_notion_tasks(service, client, task_list_id="dWtPeGlHSkQycFJzbS1CRA")

    insert_google_task_into_notion(
        service, client, task_list_id="dWtPeGlHSkQycFJzbS1CRA"
    )

    # TODO: Last one, you need to be able to get all tasklist ids from GT, avoiding the Defaul list
    # TODO Add logic to prevent user from adding a notion page with a title that already exist in GT
    tasklist_ids = [
        "dWtPeGlHSkQycFJzbS1CRA",
        "d3g2elhWNkc5UzdLNmo5Yw",
        "OTBJZnR3ZllvUUNCa3NJUA",
    ]

    remove_deleted_google_tasks(service, client, task_list_ids=tasklist_ids)
