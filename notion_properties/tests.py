from django.test import TestCase
from .dto import NotionPropertyDto


TEST_NOTION_API_RESP_PROPERTIES_DICT = {
      'Comment': {
        'id': '!vXu',
        'type': 'rich_text',
        'rich_text': []
      },
      'Amount': {
        'id': '%225%3C%7B',
        'type': 'number',
        'number': 690
      },
      'Category': {
        'id': '93%3D%3E',
        'type': 'multi_select',
        'multi_select': [
          {
            'id': '6d112c07-5a69-44d7-8d02-42895b6be454',
            'name': 'Home',
            'color': 'yellow'
          }
        ]
      },
      'Created Time': {
        'id': 'hoWJ',
        'type': 'created_time',
        'created_time': '2021-12-25T07:15:00.000Z'
      },
      'Expense': {
        'id': 'title',
        'type': 'title',
        'title': [
          {
            'type': 'text',
            'text': {
              'content': 'Rent',
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
            'plain_text': 'Rent',
            'href': None
          }
        ]
      }
    }


# Create your tests here.
class TestNotionPropertiesDtoConversions(TestCase):
    def setUp(self):
        self.id = 'helloworld'
        self.notion_type = 'checkbox'
        self.value = True
        self.name = 'test checkbox'

    def test_does_convert_from_dto_dict(self):
        dto_dict = {
            'id': self.id,
            'type': self.notion_type,
            'value': self.value,
            'name': self.name,
            'html_form_type': 'blalba',
            'html_value': 'asdfsa',
            'options': 'asdfasd'
        }
        property_dto = NotionPropertyDto.from_dto_dict(dto_dict=dto_dict)
        self.assertEqual(property_dto.id, self.id)
        self.assertEqual(property_dto.notion_type, self.notion_type)
        self.assertEqual(property_dto.value, self.value)
        self.assertEqual(property_dto.name, self.name)

    def test_deos_convert_number_from_api_resp_dict(self):
        property_dto = NotionPropertyDto.from_notion_api_property_dict(TEST_NOTION_API_RESP_PROPERTIES_DICT['Amount'],
                                                                       property_name_str='Amount')
        self.assertEqual(property_dto.name, 'Amount')
        self.assertEqual(property_dto.value, 690)
        self.assertEqual(property_dto.notion_type, 'number')
        self.assertEqual(property_dto.id, '%225%3C%7B')

    def test_deos_convert_multi_select_from_api_resp_dict(self):
        property_dto = NotionPropertyDto.from_notion_api_property_dict(TEST_NOTION_API_RESP_PROPERTIES_DICT['Category'],
                                                                       property_name_str='Category')
        self.assertEqual(property_dto.name, 'Category')
        self.assertEqual(property_dto.value, '6d112c07-5a69-44d7-8d02-42895b6be454')
        self.assertEqual(property_dto.notion_type, 'multi_select')
        self.assertEqual(property_dto.id, '93%3D%3E')

    def test_deos_convert_rich_text_from_api_resp_dict(self):
        property_dto = NotionPropertyDto.from_notion_api_property_dict(TEST_NOTION_API_RESP_PROPERTIES_DICT['Comment'],
                                                                       property_name_str='Comment')
        self.assertEqual(property_dto.name, 'Comment')
        self.assertEqual(property_dto.value, '')
        self.assertEqual(property_dto.notion_type, 'rich_text')
        self.assertEqual(property_dto.id, '!vXu')

    def test_deos_convert_title_from_api_resp_dict(self):
        property_dto = NotionPropertyDto.from_notion_api_property_dict(TEST_NOTION_API_RESP_PROPERTIES_DICT['Expense'],
                                                                       property_name_str='Expense')
        self.assertEqual(property_dto.name, 'Expense')
        self.assertEqual(property_dto.value, 'Rent')
        self.assertEqual(property_dto.notion_type, 'title')
        self.assertEqual(property_dto.id, 'title')

    def test_convert_multi_select_property_dto_to_api_create_page_dict(self):
        property_dto = NotionPropertyDto.from_notion_api_property_dict(TEST_NOTION_API_RESP_PROPERTIES_DICT['Category'],
                                                                       property_name_str='Category')
        self.assertEqual(property_dto.get_notion_property_api_dict_for_create_page_request(), [
                {
                    'id': '6d112c07-5a69-44d7-8d02-42895b6be454'
                }
            ])

    def test_convert_number_property_dto_to_create_page_api_dict(self):
        property_dto = NotionPropertyDto.from_notion_api_property_dict(TEST_NOTION_API_RESP_PROPERTIES_DICT['Amount'],
                                                                       property_name_str='Amount')
        self.assertEqual(property_dto.get_notion_property_api_dict_for_create_page_request(), 690)

    def test_convert_rich_text_property_dto_to_create_page_api_dict(self):
        property_dto = NotionPropertyDto.from_notion_api_property_dict(TEST_NOTION_API_RESP_PROPERTIES_DICT['Comment'],
                                                                       property_name_str='Comment')
        self.assertEqual(property_dto.get_notion_property_api_dict_for_create_page_request(), [{
                'text': {
                    'content': ''
                }
            }]
        )

    def test_convert_title_property_dto_to_create_page_api_dict(self):
        property_dto = NotionPropertyDto.from_notion_api_property_dict(TEST_NOTION_API_RESP_PROPERTIES_DICT['Expense'],
                                                                       property_name_str='Expense')
        self.assertEqual(property_dto.get_notion_property_api_dict_for_create_page_request(), [{
            'text': {
                'content': 'Rent'
            }
        }])
