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
# logging.basicConfig(level=logging.DEBUG)

# -----------------
# SETUP

load_dotenv()
NOTION_ID = os.getenv("NOTION_KEY")
if NOTION_ID is None:
    raise KeyError("Missing NOTION ID environment variable")
SCOPES = ["https://www.googleapis.com/auth/tasks"]

r = redis.Redis(host="localhost", port=6379, decode_responses=True)



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
            # import ipdb;ipdb.set_trace()
            # print(to_do_block)
            print(block["id"])
            checked = to_do_block["checked"]
            content = to_do_block["rich_text"][0]["plain_text"]

            if not checked:
                result["status"] = "needsAction"
            else:
                result["status"] = "completed"

            result["title"] = content
            result["id"] = block["id"]

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
    """Authentication with Google"""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("tasks", "v1", credentials=creds)
    except HttpError as err:
        logging.error(err)

    return service


# -----------------
# NOTION-GOOGLE API CALLS

def insert_notion_tasks_in_google_tasks(service, notion_tasks, task_list_id):
    """Insert notion tasks in Google, if they are not already there"""

    current_google_tasks = [
        {"google_task": task["title"],  "google_task_id": task["id"] }
        for task in service.tasks().list(tasklist=task_list_id).execute()["items"]
    ]
    # import ipdb; ipdb.set_trace()

    for notion_task in notion_tasks[::-1]:
        
        google_task_id = r.get(notion_task["id"])
        
        if notion_task["title"] not in current_google_tasks: 
            #google only knows about the title of the task, not the id. TO prevent inserting EDITED TASKS, 
            # you need to check the ids are different. No task with an existing ID should be added 
            # Problem, the id in notion and the id in google are different, cannot set googe id, 


            #SOLUTION: Use redis to store key-value pair, the key wil be the id Notion generates 
            # and will match the Google generated id

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


def add_id_mapping_to_redis(service, notion_tasks, task_list_id):
    """Add key-value mapping between Notion todo ids and Google todo ids"""

    current_google_tasks = [
        {"title": task["title"], "id": task["id"], "status": task["status"]}
        for task in service.tasks().list(tasklist=task_list_id).execute()["items"]
    ]

    for notion_task in notion_tasks:
        for google_task in current_google_tasks:
            
            if r.get(notion_task["id"]):
                logging.info("ID already in Redis, skipping")
                continue

            elif notion_task["title"] == google_task["title"] and notion_task['status'] == google_task['status']:
                r.set(notion_task['id'], google_task['id'])
                logging.info(f"Successfully added k: {notion_task['id']} v: {google_task['id']}")


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

    import ipdb;ipdb.set_trace()
    # If redis is empty, add all data
    if not r.keys(): # replace .keys() with something different later
        logging.info("Adding new data to Redis")
        add_id_mapping_to_redis(service, notion_tasks, TASK_LIST_ID )


    insert_notion_tasks_in_google_tasks(service, notion_tasks, TASK_LIST_ID)
    # update_google_tasks(service, notion_tasks, TASK_LIST_ID)



# Extra features:
# Fix the bug of adding a new task, when an existing one in Notion has changed, you only need to, you will have to use the ID


# If a task is ticked on Google Calendar, it should be ticket on Notion as well
# Add Tests 
# CI/CD
# Add docs how to set it up
# add try, except and Logging 
# When a task is deleted in Notion -> dete it in Google tasks as well