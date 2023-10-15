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

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

NOTION_ID = os.getenv("NOTION_KEY")

if NOTION_ID is None:
    raise KeyError("Missing NOTION ID environment variable")

SCOPES = ["https://www.googleapis.com/auth/tasks"]

# -----------------
# NOTION FUNCTIONS

def get_all_pages(client: Client) -> List[str]:
    """Get all pages that have enabled the integration"""
    
    page_ids = []
    for page in client.search()["results"]:
        page_ids.append(page["id"])
    
    if not page_ids:
        logging.info("No notion pages have enabled the integration")

    return page_ids
    

def get_all_blocks(client: Client, page_id: str) -> List[Dict[str,str]]:
    """Get all blocks on the page given via page_id"""
    response = client.blocks.children.list(block_id=page_id)
    return response["results"]


def get_todo(client: Client, all_blocks: List[Dict[str,str]]):
    """Get all todo blocks given a list of blocks"""
    to_do_blocks = []
    for block in all_blocks:
        result = {}
        if block["type"] == "to_do":
            to_do_block = block["to_do"]
            checked = to_do_block["checked"]
            content = to_do_block["rich_text"][0]["plain_text"]

            if not checked:
                result["status"] = "needsAction"
            else:
                result["status"] = "completed"

            result["title"] = content

            to_do_blocks.append(result)

        if block["has_children"]:
            nested_block = get_all_blocks(client, block["id"])
            nested_result = get_todo(client, nested_block)
            to_do_blocks.extend(nested_result)

    if not to_do_blocks:
        logging.info("No Todo blocks have been found")

    return to_do_blocks


# -----------------
# AUTH FUNCTION

def authenticate_and_print():
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("tasks", "v1", credentials=creds)
    except HttpError as err:
        print(err)

    return service


# -----------------
# NOTION-GOOGLE API CALLS

def insert_notion_tasks_in_google_tasks(service, notion_tasks, task_list_id):
    """Function to insert notion tasks in Google, if they are not already there"""

    current_google_tasks = [
        task["title"]
        for task in service.tasks().list(tasklist=task_list_id).execute()["items"]
    ]

    for notion_task in notion_tasks[::-1]:

        if notion_task["title"] not in current_google_tasks:

            service.tasks().insert(tasklist=task_list_id, body=notion_task).execute()


def update_google_tasks(service, notion_tasks, task_list_id):

    """Function that Updates tasks. Closes tasks marked as completed from Notion to Google Takss"""

    current_google_tasks = [
        {"title": task["title"], "id": task["id"], "status": task["status"]}
        for task in service.tasks().list(tasklist=task_list_id).execute()["items"]
    ]

    for notion_task in notion_tasks:

        for google_task in current_google_tasks:
            if google_task["title"] == notion_task["title"]:

                service.tasks().patch(
                    tasklist=task_list_id, task=google_task["id"], body=notion_task
                ).execute()
            continue


service = authenticate_and_print()


def create_notion_tasklist() -> str:
    """Create a dedicated TaskList in Google Tasks if it does not exist"""

    for task_list in service.tasklists().list().execute()["items"]:
        if task_list["title"] == "Tasks from Notion":
            return task_list["id"]

    new_task_list = (
        service.tasklists().insert(body={"title": "Tasks from Notion"}).execute()
    )
    return new_task_list["id"]


if __name__ == "__main__":

    # Create Client 
    client = Client(auth=NOTION_ID)

    # Get all page ids
    page_ids = get_all_pages(client)

    # Get every block from each page id
    all_blocks = []
    for page_id in page_ids:
        all_blocks.extend(get_all_blocks(client, page_id))

    pprint(get_todo(client, all_blocks))

    # Get all todos
    notion_tasks = get_todo(client, all_blocks)

    TASK_LIST_ID = create_notion_tasklist()

    insert_notion_tasks_in_google_tasks(service, notion_tasks, TASK_LIST_ID)
    update_google_tasks(service, notion_tasks, TASK_LIST_ID)



# Extra features:
# Fix the bug of adding a new task, when an existing one in Notion has changed, you only need to, you will have to use the ID
# If a task is ticked on Google Calendar, it should be ticket on Notion as well
# Add Tests 
# CI/CD
# Add docs how to set it up
# add try, except and Logging 
# When a task is deleted in Notion -> dete it in Google tasks as well