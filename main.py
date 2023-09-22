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

            result["checked"]=checked
            result["content"]=content

            to_do_blocks.append(result)

        if block["has_children"]:
            nested_block = get_all_blocks(client, block["id"])
            nested_result = get_todo(client, nested_block)
            to_do_blocks.extend(nested_result)


    return to_do_blocks



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

        # Call the Tasks API
        results = service.tasklists().list(maxResults=10).execute()
        items = results.get('items', [])

        if not items:
            print('No task lists found.')
            return

        print('Task lists:')
        for item in items:
            print(u'{0} ({1})'.format(item['title'], item['id']))
    except HttpError as err:
        print(err)



def insert_notion_tasks_in_google_tasks():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('tasks', 'v1', credentials=creds)


tasklist = "list2"
INSERT_LIST = f"https://tasks.googleapis.com/tasks/v1/lists/{tasklist}/tasks"

if __name__ == "__main__":

    client = Client(auth=NOTION_ID)
    all_blocks = get_all_blocks(client, PAGE_ID)

    # pprint(all_blocks)
    pprint(get_todo(client, all_blocks))
    # main()

