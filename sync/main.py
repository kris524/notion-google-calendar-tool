# import all necessary functions/classes from both files for a single run script


# if __name__ == "__main__":

#     load_dotenv()
#     NOTION_ID = os.getenv("NOTION_KEY")  #NOTION_KEY
#     if NOTION_ID is None:
#         raise KeyError("Missing NOTION ID environment variable")

#     service = authenticate_and_print()

#     # Create Client
#     client = Client(auth=NOTION_ID)

#     # Get all page ids
#     page_ids = get_all_pages(client)

#     # Get every block from each page id
#     all_blocks = []
#     for page_id in page_ids:
#         all_blocks.extend(get_all_blocks(client, page_id))

#     # Get all Notion todos
#     notion_tasks = get_todo(client, all_blocks)

#     TASK_LIST_ID = create_notion_tasklist(service)

#     # Insert tasks from Notion to Google
#     insert_notion_tasks_in_google_tasks(service, notion_tasks, TASK_LIST_ID)

#     # TODO replace .keys() with something more efficient later
#     # If redis is empty, or new todo has been added, update the database
#     if not r.keys() or len(r.keys()) < len(notion_tasks):  # add a
#         logging.info("Adding new data to Redis")
#         add_id_mapping_to_redis(service, notion_tasks, TASK_LIST_ID)

#     # If redis has more keys than current notion_tasks, delete the Google task and that key
#     if len(r.keys()) > len(notion_tasks):
#         logging.info("Deleting tasks")
#         remove_deleted_tasks_ids_from_redis(service, notion_tasks, TASK_LIST_ID)

#     # Update the state of tasks, whenever needed (checked, changed name, etc.)
#     update_google_tasks(service, notion_tasks, TASK_LIST_ID)
