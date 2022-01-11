import json

VALID_DATABASE_ID = 'a9f68551-1cf2-4615-9a41-1f1368ae4f78'
VALID_NOTION_TASK_ID = 'b55c9c91-384d-452b-81db-d1ef79372b75'
VALID_ACCESS_TOKEN = 'access_123'
VALID_ACCESS_TOKEN_2 = 'access_122'

MOCK_DATABASE_RESPONSE = {
    'object': 'list',
    'results': [
        {
            'object': 'database',
            'id': 'a9f68551-1cf2-4615-9a41-1f1368ae4f78',
            'cover': None,
            'icon': {
                'type': 'emoji',
                'emoji': '✅'
            },
            'created_time': '2021-09-12T17:03:00.000Z',
            'last_edited_time': '2021-12-31T13:03:00.000Z',
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'Todo',
                        'link': None
                    },
                    'annotations': {
                        'bold': False,
                        'italic': False,
                        'strikethrough': False,
                        'underline': False,
                        'code': False,
                        'color': 'default'
                    },
                    'plain_text': 'Todo',
                    'href': None
                }
            ],
            'properties': {
                'Property 2': {
                    'id': 'E%3F%5EI',
                    'name': 'Property 2',
                    'type': 'email',
                    'email': {}
                },
                'Deadline': {
                    'id': 'Fq%3Ar',
                    'name': 'Deadline',
                    'type': 'date',
                    'date': {}
                },
                'Property 3': {
                    'id': 'SXQ%7B',
                    'name': 'Property 3',
                    'type': 'phone_number',
                    'phone_number': {}
                },
                'Status': {
                    'id': '%60moG',
                    'name': 'Status',
                    'type': 'select',
                    'select': {
                        'options': [
                            {
                                'id': '1',
                                'name': 'Not started',
                                'color': 'red'
                            },
                            {
                                'id': '2',
                                'name': 'In progress',
                                'color': 'yellow'
                            },
                            {
                                'id': '3',
                                'name': 'Completed',
                                'color': 'green'
                            }
                        ]
                    }
                },
                'Assign': {
                    'id': 'd%60Tf',
                    'name': 'Assign',
                    'type': 'people',
                    'people': {}
                },
                'Property 1': {
                    'id': 'qsTb',
                    'name': 'Property 1',
                    'type': 'url',
                    'url': {}
                },
                'Property': {
                    'id': 'uJCH',
                    'name': 'Property',
                    'type': 'number',
                    'number': {
                        'format': 'number'
                    }
                },
                'Property 4': {
                    'id': '%7CJhi',
                    'name': 'Property 4',
                    'type': 'rich_text',
                    'rich_text': {}
                },
                'Name': {
                    'id': 'title',
                    'name': 'Name',
                    'type': 'title',
                    'title': {}
                }
            },
            'parent': {
                'type': 'page_id',
                'page_id': '0d4ba6e3-e066-40a7-9746-8bd1404bb786'
            },
            'url': 'https://www.notion.so/a9f685511cf246159a411f1368ae4f78'
        },
        {
            'object': 'database',
            'id': 'c8fc8363-81cc-4197-a0fa-7deb00dbd43d',
            'cover': None,
            'icon': None,
            'created_time': '2021-10-05T15:31:00.000Z',
            'last_edited_time': '2021-12-30T15:20:00.000Z',
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'Expenses',
                        'link': None
                    },
                    'annotations': {
                        'bold': False,
                        'italic': False,
                        'strikethrough': False,
                        'underline': False,
                        'code': False,
                        'color': 'default'
                    },
                    'plain_text': 'Expenses',
                    'href': None
                }
            ],
            'properties': {
                'Comment': {
                    'id': '!vXu',
                    'name': 'Comment',
                    'type': 'rich_text',
                    'rich_text': {}
                },
                'Amount': {
                    'id': '%225%3C%7B',
                    'name': 'Amount',
                    'type': 'number',
                    'number': {
                        'format': 'euro'
                    }
                },
                'Category': {
                    'id': '93%3D%3E',
                    'name': 'Category',
                    'type': 'multi_select',
                    'multi_select': {
                        'options': [
                            {
                                'id': '6d112c07-5a69-44d7-8d02-42895b6be454',
                                'name': 'Home',
                                'color': 'yellow'
                            },
                            {
                                'id': '0f13705c-cbca-4579-aed5-8ec85ce10d0e',
                                'name': 'Groceries',
                                'color': 'red'
                            },
                            {
                                'id': '38d0a3a6-7ac1-493e-81d3-80a4733d0462',
                                'name': 'Entertainment',
                                'color': 'blue'
                            },
                            {
                                'id': 'c94ed273-1529-432d-b383-717c6d687703',
                                'name': 'Restaurant/Eating Out',
                                'color': 'orange'
                            },
                            {
                                'id': '45662df9-0c78-4344-85e5-224b6aff2872',
                                'name': 'Transportation',
                                'color': 'pink'
                            },
                            {
                                'id': 'ed94c1d9-76db-433f-ad0f-464a45640a79',
                                'name': 'Gifts',
                                'color': 'brown'
                            },
                            {
                                'id': '966b8a12-81a1-4ec7-a361-0fdc92d9540f',
                                'name': 'Business',
                                'color': 'green'
                            }
                        ]
                    }
                },
                'Created Time': {
                    'id': 'hoWJ',
                    'name': 'Created Time',
                    'type': 'created_time',
                    'created_time': {}
                },
                'Expense': {
                    'id': 'title',
                    'name': 'Expense',
                    'type': 'title',
                    'title': {}
                }
            },
            'parent': {
                'type': 'page_id',
                'page_id': '6df7faeb-c32d-44e6-8c02-37be212f56b2'
            },
            'url': 'https://www.notion.so/c8fc836381cc4197a0fa7deb00dbd43d'
        },
        {
            'object': 'database',
            'id': 'd175c54b-e3e5-43cb-a7a0-8fe31fcf505a',
            'cover': None,
            'icon': None,
            'created_time': '2021-12-16T17:12:00.000Z',
            'last_edited_time': '2021-12-28T09:03:00.000Z',
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'Habit Tracker',
                        'link': None
                    },
                    'annotations': {
                        'bold': False,
                        'italic': False,
                        'strikethrough': False,
                        'underline': False,
                        'code': False,
                        'color': 'default'
                    },
                    'plain_text': 'Habit Tracker',
                    'href': None
                }
            ],
            'properties': {
                'Completed': {
                    'id': 'Gwjd',
                    'name': 'Completed',
                    'type': 'checkbox',
                    'checkbox': {}
                },
                'Category': {
                    'id': 'H%40%5Bt',
                    'name': 'Category',
                    'type': 'select',
                    'select': {
                        'options': [
                            {
                                'id': '8547ff50-8fa9-426f-b3ed-d9184df02d79',
                                'name': 'Well-Being',
                                'color': 'default'
                            }
                        ]
                    }
                },
                'Priority': {
                    'id': 'M%5EM%5C',
                    'name': 'Priority',
                    'type': 'select',
                    'select': {
                        'options': [
                            {
                                'id': '7e350941-779a-498e-a787-ce1517b7f444',
                                'name': 'High',
                                'color': 'blue'
                            }
                        ]
                    }
                },
                'Property': {
                    'id': '%5DO%3CR',
                    'name': 'Property',
                    'type': 'created_time',
                    'created_time': {}
                },
                'Name': {
                    'id': 'title',
                    'name': 'Name',
                    'type': 'title',
                    'title': {}
                }
            },
            'parent': {
                'type': 'workspace',
                'workspace': True
            },
            'url': 'https://www.notion.so/d175c54be3e543cba7a08fe31fcf505a'
        },
        {
            'object': 'database',
            'id': '760b7f25-af14-4ef3-8d01-ddb2652362ca',
            'cover': None,
            'icon': {
                'type': 'emoji',
                'emoji': '📹'
            },
            'created_time': '2021-11-15T20:51:00.000Z',
            'last_edited_time': '2021-12-16T12:38:00.000Z',
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'Upcoming Videos',
                        'link': None
                    },
                    'annotations': {
                        'bold': False,
                        'italic': False,
                        'strikethrough': False,
                        'underline': False,
                        'code': False,
                        'color': 'default'
                    },
                    'plain_text': 'Upcoming Videos',
                    'href': None
                }
            ],
            'properties': {
                'Completion': {
                    'id': 'RiGH',
                    'name': 'Completion',
                    'type': 'multi_select',
                    'multi_select': {
                        'options': [
                            {
                                'id': '6cd01489-8438-45bb-bbce-9dc0610d7036',
                                'name': 'Not Started',
                                'color': 'orange'
                            },
                            {
                                'id': '44b23497-1d0e-47b1-a822-ef9a4833b7d7',
                                'name': 'Done',
                                'color': 'green'
                            },
                            {
                                'id': 'a9e3a355-f13e-4c0e-9e64-52b15b39b896',
                                'name': 'Ready To Upload',
                                'color': 'pink'
                            },
                            {
                                'id': 'b4603396-c4a6-4e1c-b982-e095c1e29c96',
                                'name': 'Ready For Post Processing',
                                'color': 'default'
                            },
                            {
                                'id': '3d0eeb6b-186f-420e-89d4-e6c76ec8a117',
                                'name': 'Scheduled',
                                'color': 'brown'
                            },
                            {
                                'id': '55db528b-2252-40c9-8f35-154f73988345',
                                'name': 'Ready To Record',
                                'color': 'yellow'
                            },
                            {
                                'id': 'e218b9b8-63e0-4d59-80b7-766773ed60f9',
                                'name': 'Ready To Edit',
                                'color': 'purple'
                            },
                            {
                                'id': 'f9af3a88-12ca-4579-b32f-6ecc4dd0a839',
                                'name': 'Backlog Idea',
                                'color': 'red'
                            }
                        ]
                    }
                },
                'Sub Tutorials': {
                    'id': 'bmeb',
                    'name': 'Sub Tutorials',
                    'type': 'relation',
                    'relation': {
                        'database_id': '760b7f25-af14-4ef3-8d01-ddb2652362ca',
                        'synced_property_name': 'Included In Tutorials',
                        'synced_property_id': 'ynUH'
                    }
                },
                'Thumbnail': {
                    'id': 'ot%3B%5B',
                    'name': 'Thumbnail',
                    'type': 'files',
                    'files': {}
                },
                'Presentation': {
                    'id': 'xtOi',
                    'name': 'Presentation',
                    'type': 'rich_text',
                    'rich_text': {}
                },
                'Included In Tutorials': {
                    'id': 'ynUH',
                    'name': 'Included In Tutorials',
                    'type': 'relation',
                    'relation': {
                        'database_id': '760b7f25-af14-4ef3-8d01-ddb2652362ca',
                        'synced_property_name': 'Sub Tutorials',
                        'synced_property_id': 'bmeb'
                    }
                },
                'Name': {
                    'id': 'title',
                    'name': 'Name',
                    'type': 'title',
                    'title': {}
                }
            },
            'parent': {
                'type': 'page_id',
                'page_id': '2d581612-5c64-4457-afcf-6610aca420f3'
            },
            'url': 'https://www.notion.so/760b7f25af144ef38d01ddb2652362ca'
        },
        {
            'object': 'database',
            'id': '97b03397-6f82-4709-93ea-93661365628f',
            'cover': None,
            'icon': {
                'type': 'emoji',
                'emoji': '🕌'
            },
            'created_time': '2021-10-13T18:24:00.000Z',
            'last_edited_time': '2021-12-13T09:43:00.000Z',
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'Trip Dubai',
                        'link': None
                    },
                    'annotations': {
                        'bold': False,
                        'italic': False,
                        'strikethrough': False,
                        'underline': False,
                        'code': False,
                        'color': 'default'
                    },
                    'plain_text': 'Trip Dubai',
                    'href': None
                }
            ],
            'properties': {
                'Zeit': {
                    'id': 'ME%3DX',
                    'name': 'Zeit',
                    'type': 'date',
                    'date': {}
                },
                'Status': {
                    'id': '%5BpM%40',
                    'name': 'Status',
                    'type': 'select',
                    'select': {
                        'options': [
                            {
                                'id': '1',
                                'name': 'Todo',
                                'color': 'red'
                            },
                            {
                                'id': '2',
                                'name': 'Gebucht',
                                'color': 'yellow'
                            },
                            {
                                'id': '3',
                                'name': 'Completed',
                                'color': 'green'
                            }
                        ]
                    }
                },
                'Property': {
                    'id': '%5EI%3Dz',
                    'name': 'Property',
                    'type': 'rich_text',
                    'rich_text': {}
                },
                'Assign': {
                    'id': '%5Em%7Ch',
                    'name': 'Assign',
                    'type': 'people',
                    'people': {}
                },
                'Name': {
                    'id': 'title',
                    'name': 'Name',
                    'type': 'title',
                    'title': {}
                }
            },
            'parent': {
                'type': 'page_id',
                'page_id': '0d4ba6e3-e066-40a7-9746-8bd1404bb786'
            },
            'url': 'https://www.notion.so/97b033976f82470993ea93661365628f'
        },
        {
            'object': 'database',
            'id': 'd2a24d67-8fa5-44df-a26e-82ab2334b1a6',
            'cover': None,
            'icon': None,
            'created_time': '2021-11-23T21:12:00.000Z',
            'last_edited_time': '2021-11-23T21:31:00.000Z',
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'Competition',
                        'link': None
                    },
                    'annotations': {
                        'bold': False,
                        'italic': False,
                        'strikethrough': False,
                        'underline': False,
                        'code': False,
                        'color': 'default'
                    },
                    'plain_text': 'Competition',
                    'href': None
                }
            ],
            'properties': {
                'Aktiv': {
                    'id': '%3Fawy',
                    'name': 'Aktiv',
                    'type': 'checkbox',
                    'checkbox': {}
                },
                'YouTube Link': {
                    'id': 'WS%7BT',
                    'name': 'YouTube Link',
                    'type': 'url',
                    'url': {}
                },
                'Name': {
                    'id': 'title',
                    'name': 'Name',
                    'type': 'title',
                    'title': {}
                }
            },
            'parent': {
                'type': 'page_id',
                'page_id': '2d581612-5c64-4457-afcf-6610aca420f3'
            },
            'url': 'https://www.notion.so/d2a24d678fa544dfa26e82ab2334b1a6'
        },
        {
            'object': 'database',
            'id': 'f7693e94-a80b-4b79-8f85-bcea7406002f',
            'cover': None,
            'icon': {
                'type': 'emoji',
                'emoji': '📣'
            },
            'created_time': '2021-11-18T08:43:00.000Z',
            'last_edited_time': '2021-11-18T08:44:00.000Z',
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'Brand Tasks',
                        'link': None
                    },
                    'annotations': {
                        'bold': False,
                        'italic': False,
                        'strikethrough': False,
                        'underline': False,
                        'code': False,
                        'color': 'default'
                    },
                    'plain_text': 'Brand Tasks',
                    'href': None
                }
            ],
            'properties': {
                'Assign': {
                    'id': 'IB%5E%7C',
                    'name': 'Assign',
                    'type': 'people',
                    'people': {}
                },
                'Status': {
                    'id': 'g%3E%7CK',
                    'name': 'Status',
                    'type': 'select',
                    'select': {
                        'options': [
                            {
                                'id': '1',
                                'name': 'Not started',
                                'color': 'red'
                            },
                            {
                                'id': '2',
                                'name': 'In progress',
                                'color': 'yellow'
                            },
                            {
                                'id': '3',
                                'name': 'Completed',
                                'color': 'green'
                            }
                        ]
                    }
                },
                'Name': {
                    'id': 'title',
                    'name': 'Name',
                    'type': 'title',
                    'title': {}
                }
            },
            'parent': {
                'type': 'page_id',
                'page_id': '2d581612-5c64-4457-afcf-6610aca420f3'
            },
            'url': 'https://www.notion.so/f7693e94a80b4b798f85bcea7406002f'
        }
    ],
    'next_cursor': None,
    'has_more': False
}


class NotionApiMockNotFoundException(Exception):
    pass


class NotionApiMockUnauthorizedException(Exception):
    pass


class NotionApiMockBadRequestException(Exception):
    pass


def create_or_get_mocked_oauth_notion_client(*args, **kwargs):
    class MockDatabasesApi:
        def __init__(self, is_valid_token):
            self.is_valid_token = is_valid_token

        def retrieve(self, database_id):
            if not self.is_valid_token:
                raise Exception('Invalid token!')
            if database_id == VALID_DATABASE_ID:
                # return the first database
                return MOCK_DATABASE_RESPONSE['results'][0]
            else:
                raise Exception('Invalid Database ID')

    class MockPagesApi:
        def __init__(self, is_valid_token):
            self.is_valid_token = is_valid_token

        def create(self, properties, parent):
            # TODO: Check for specifics?
            pass

    class MockClient:
        def __init__(self, token):
            self.page_api_mock = None
            self.database_api_mock = None
            self.token = token

        @property
        def client_token_is_valid(self):
            return self.token == VALID_ACCESS_TOKEN or self.token == VALID_ACCESS_TOKEN_2

        @property
        def databases(self):
            self.database_api_mock = MockDatabasesApi(is_valid_token=self.client_token_is_valid)
            return self.database_api_mock

        @property
        def pages(self):
            self.page_api_mock = MockPagesApi(is_valid_token=self.client_token_is_valid)
            return self.page_api_mock

        def search(self, filter, page_size):
            if not self.client_token_is_valid:
                raise Exception('Invalid client token!')
            if 'property' not in filter or 'value' not in filter:
                raise Exception('Invalid filter format!')
            if 'object' != filter['property'] or 'database' != filter['value']:
                raise Exception('Invalid values!')
            return MOCK_DATABASE_RESPONSE

    access_token = kwargs['auth']
    return MockClient(access_token)
