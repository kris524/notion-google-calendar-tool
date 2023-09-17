import os
from notion_client import Client
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()


NOTION_ID = os.getenv("NOTION_KEY")
PAGE_ID = os.getenv("NOTION_PAGE_ID")

client = Client(auth=NOTION_ID)

all_users = client.users.list()

page = client.pages.retrieve(PAGE_ID)


def read_text(client, page_id):
    response = client.blocks.children.list(block_id=page_id)
    return response["results"]

# pprint(page)
print("----------------------------")
pprint(read_text(client, PAGE_ID))
print("----------------------------")



