from threading import Thread

from notion_database.service import query_user_notion_databases_list


class FetchUserDatabasesThread(Thread):
    def __init__(self, user_model):
        super().__init__()
        self.user_model = user_model
        self.response_simple_database_dict = []

    def run(self):
        self.response_simple_database_dict = query_user_notion_databases_list(
            user_model=self.user_model
        )
