from workspaces.models import NotionWorkspaceAccess

import notion_client
import logging
from django.utils.timezone import now

# Get an instance of a logger
logger = logging.getLogger(__name__)


class NotionApiException(Exception):
    pass


IGNORED_PROPERTIES_SET = {
    'relation', 'formula', "rollup", "created_time", "created_by", "last_edited_time", "last_edited_by", "people",
    "files"
}

NOTION_TEXT_PROPERTIES_SET = { 'email', 'phone_number', 'rich_text', 'title' }

NOTION_SELECT_PROPERTIES = { 'multi_select', 'select' }

NOTION_DATE_PROPERTIES_SET = {'last_edited_time', 'created_time', 'date'}


class NotionPropertyContainer:
    def __init__(self, property_dict, name):
        self.name = name
        self.id = property_dict['id']
        self.notion_type = property_dict['type']
        if self.notion_type in property_dict:
            self.value = property_dict[self.notion_type]
        else:
            self.value = get_default_value_by_notion_property_type(notion_property_type_str=self.notion_type)

    @property
    def notion_type_as_html_form_type(self):
        if self.notion_type in NOTION_TEXT_PROPERTIES_SET or self.notion_type in NOTION_SELECT_PROPERTIES:
            return 'text'
        if self.notion_type in NOTION_DATE_PROPERTIES_SET:
            return 'datetime-local'
        # only expecting 'checkbox' and 'number' to remain as possible values
        return self.notion_type

    def dict(self):
        return {
            'id': self.id,
            'type': self.notion_type,
            'value': self.value,
            'name': self.name
        }


def load_user_notion_client(user_model):
    notion_workspace_access_grant_model = NotionWorkspaceAccess.objects.filter(owner=user_model).first()
    if notion_workspace_access_grant_model is None:
        raise NotionApiException(f'User {user_model.username} does not have any access grants!')
    logger.info(f'Fetching Notion Database with Access Token {notion_workspace_access_grant_model.access_token}')
    return notion_client.Client(auth=notion_workspace_access_grant_model.access_token)


def query_user_notion_databases_list(user_model, query_string):
    logger.info(f'Fetching workspace pages')
    request_filter_dict = {"filter": {"property": "object", "value": "database"}, "page_size": 100}
    if query_string is not None and len(query_string) > 0:
        request_filter_dict['query'] = query_string
    response_dict = load_user_notion_client(user_model=user_model).search(**request_filter_dict)
    if 'results' not in response_dict:
        raise NotionApiException('Unable to retrieve Database data!')
    properties_dict = response_dict.get('results')
    return [convert_notion_database_resp_dict_to_simple_database_dict(database_dict) for database_dict
            in properties_dict]


def query_user_notion_database_by_id(user_model, database_id_str):
    database_dict = load_user_notion_client(user_model=user_model).databases.retrieve(database_id=database_id_str)
    return convert_notion_database_resp_dict_to_simple_database_dict(database_dict)


def convert_notion_database_resp_dict_to_simple_database_dict(notion_db_dict):
    property_dict_list = []
    for property_name in notion_db_dict['properties'].keys():
        notion_property_dict = notion_db_dict['properties'][property_name]
        # certain property types are not supported
        if notion_property_dict['type'] in IGNORED_PROPERTIES_SET:
            continue
        property_dict_list.append(NotionPropertyContainer(property_dict=notion_property_dict, name=property_name))
    return {
        'name': notion_db_dict['title'][0]['text']['content'],
        'id': notion_db_dict['id'],
        'properties': property_dict_list
    }


def get_default_value_by_notion_property_type(notion_property_type_str):
    if notion_property_type_str in NOTION_TEXT_PROPERTIES_SET or notion_property_type_str in NOTION_SELECT_PROPERTIES:
        return ''
    if notion_property_type_str in NOTION_DATE_PROPERTIES_SET:
        return now()
    return None