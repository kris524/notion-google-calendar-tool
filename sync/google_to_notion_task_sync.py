"""Script that handles the sync from Google Tasks to Notion"""
import os
from notion_client import Client
from pprint import pprint
from dotenv import load_dotenv
from typing import List, Dict
import os.path
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import redis
from notion_to_google_task_sync import authenticate_and_print

# Extra features:
# (???) If a task is added to GC, it should be added to Notion as well (???) Where?
# TODO: Currently you have a Many-to-one relationship, you might want to have a to One-to-one relationship
# This is what we want to work on now, we cant establish a true two way connection until we have one to one mapping



# TODO: Also, update the redis db to have the reverse mapping, map from G id to N id

# DONE If a task is ticked on Google Calendar, it should be ticket on Notion as well, etc.
# DONE If a task is changed (text edited) in GC it should be changed in Notion as well
# TODO If a task is deleted on GC, if should be deleted in Notion as well


def insert_google_task_into_notion(service, task_list_id):
    """Insert google tasks into notion"""
    current_google_tasks = [
        {"title": task["title"], "id": task["id"], "status": task["status"]}
        for task in service.tasks().list(tasklist=task_list_id).execute()["items"]
    ]
    


if __name__ == "__main__":
    load_dotenv()
    NOTION_ID = os.getenv("NOTION_KEY") 

    client = Client(auth=NOTION_ID)
    service = authenticate_and_print()

    # this is the functionality that needs to be generalised in a function, 
    # this will be used for changed text and tick box changes
    block = client.blocks.retrieve("0f3d06aa-4a00-4ce8-81cd-02e9ea24efb1")
    print(block)
    block["to_do"]["checked"] = False
    block["to_do"]["rich_text"][0]["text"]["content"] = "Hello World"

    client.blocks.update("0f3d06aa-4a00-4ce8-81cd-02e9ea24efb1", **block)

    print(block)
    # insert_google_task_into_notion(service, task_list_id)