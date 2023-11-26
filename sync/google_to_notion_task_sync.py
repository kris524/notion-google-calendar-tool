"""Script that handles the sync from Google Tasks to Notion"""
import os
from notion_client import Client
from dotenv import load_dotenv
import os.path

from notion_to_google_task_sync import authenticate_and_print
from notion_to_google_task_sync import r_reverse



# DONE: Also, update the redis db to have the reverse mapping, map from G id to N id
# DONE If a task is ticked on Google Calendar, it should be ticket on Notion as well, etc.
# DONE If a task is changed (text edited) in GC it should be changed in Notion as well
# TODO If a task is added in GC, add it to Notion, corresponding page AND redis
# TODO If a task is deleted on GC, if should be deleted in Notion as well AND in the database


# def insert_google_task_into_notion(service, task_list_id):
#     """Insert google tasks into notion"""
#     current_google_tasks = [
#         {"title": task["title"], "id": task["id"], "status": task["status"]}
#         for task in service.tasks().list(tasklist=task_list_id).execute()["items"]
#     ]



def update_notion_tasks(service, client, task_list_id):
    """Function that Updates tasks. Closes tasks marked as completed from Notion to Google Takss"""

    current_google_tasks = [
        {"title": task["title"], "id": task["id"], "status": task["status"]}
        for task in service.tasks().list(tasklist=task_list_id, showHidden=True).execute()["items"]
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

    # this is the functionality that needs to be generalised in a function, 
    # this will be used for changed text and tick box changes
    # insert_google_task_into_notion(service, task_list_id)
    # import ipdb;ipdb.set_trace()
    update_notion_tasks(service, client, task_list_id="eEctUkkwdGctZ3Q1d3RoQg")

    tasklists_id = ["eEctUkkwdGctZ3Q1d3RoQg", "TXN4Y01pN2FOTk9kTnpUbw", "aXBIaHhfNVMzeGo5VWVncg"]