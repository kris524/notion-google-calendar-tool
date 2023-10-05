import os
from notion_client import Client
from pprint import pprint
from dotenv import load_dotenv

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


load_dotenv()

NOTION_ID = os.getenv("NOTION_KEY")
PAGE_ID = os.getenv("NOTION_PAGE_ID")
SCOPES = ['https://www.googleapis.com/auth/tasks']

#-----------------
# NOTION FUNCTIONS
def get_all_blocks(client, page_id):
    """Get all blocks on the page given via page_id"""
    response = client.blocks.children.list(block_id=page_id)
    return response["results"]



def get_todo(client, all_blocks):
    """Get all todo blocks given a list of blocks"""
    to_do_blocks = []
    for block in all_blocks:
        result = {}
        if block["type"]=="to_do":
            to_do_block = block["to_do"]
            checked = to_do_block["checked"]
            content = to_do_block["rich_text"][0]["plain_text"]

            if not checked:
                result["status"] = "needsAction"
            else:
                result["status"] = "completed"

            result["title"]=content

            to_do_blocks.append(result)

        if block["has_children"]:
            nested_block = get_all_blocks(client, block["id"])
            nested_result = get_todo(client, nested_block)
            to_do_blocks.extend(nested_result)


    return to_do_blocks

def get_all_notion_todos_all_pages():
    ...


#-----------------
# GOOGLE FUNCTIONS

def authenticate_and_print():
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('tasks', 'v1', credentials=creds)
    except HttpError as err:
        print(err)

    return service


def insert_notion_tasks_in_google_tasks(service, notion_tasks):

    res = service.tasks().list(tasklist="NzY5SkRySG5xMVRBU1VVTQ").execute()
    items = res.get('items', [])
    pprint(items)
    for notion_task in notion_tasks:
        # if notion_task["title"] 
        service.tasks().insert(tasklist="NzY5SkRySG5xMVRBU1VVTQ", body=notion_task).execute()


def update_google_tasks():
    ...

def create_notion_tasklist():
    ...


service = authenticate_and_print()

if __name__ == "__main__":

    client = Client(auth=NOTION_ID)
    all_blocks = get_all_blocks(client, PAGE_ID)


    pprint(get_todo(client, all_blocks))
    notion_tasks = get_todo(client, all_blocks)
    insert_notion_tasks_in_google_tasks(service, notion_tasks)



#TODO: NEXT STEPS:

# you will create a new list called notion tasks if it doesnt exist 
# and add all tasks from all notion pages there. so its a Many to One relation 
# (Every notion page that has a todo, we take the todo and add it to a single Google tasks list called notion tasks)


#If a task is ticked on Google Calendar, it should be ticket on Notion as well, same vice versa
# 
# (???) We want to develop functionality that If a task is created on Notion, it appears on GC, but what if we create a task in GC? Do we want it to appear in Notion? (Two way communication?)

# Do we need a database or anything other that this code?