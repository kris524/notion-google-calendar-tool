import os
from notion_client import Client
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()


NOTION_ID = os.getenv("NOTION_KEY")
PAGE_ID = os.getenv("NOTION_PAGE_ID")



def get_all_blocks(client, page_id):
    response = client.blocks.children.list(block_id=page_id)
    return response["results"]



def get_todo(client, all_blocks):

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




if __name__ == "__main__":
    client = Client(auth=NOTION_ID)

    all_blocks = get_all_blocks(client, PAGE_ID)

    # pprint(all_blocks)
    pprint(get_todo(client, all_blocks))


