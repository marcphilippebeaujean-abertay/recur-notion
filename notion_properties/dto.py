from django.utils.timezone import now

from .constants import (
    EMPTY_OPTION_DICT,
    IGNORED_PROPERTIES_SET,
    NOTION_DATE_PROPERTIES_SET,
    NOTION_SELECT_PROPERTIES,
    NOTION_TEXT_PROPERTIES_SET,
)


# This class is a DTO (Data Transfer Object) responsible for holding and converting notion properties between different Formats.
#    1. The default API format returned from Notion API
#    2. A simpler format we can use in HTML templates and to store in the database
# The reason we need this is that otherwise, a lot of complex business logic would need to take place in the
# jinja templates.
class NotionPropertyDto:
    def __init__(
        self,
        id_str,
        notion_type_str,
        name_str,
        assign_default_value,
        options_list=None,
        value=None,
    ):
        self.name = name_str
        self.id = id_str
        self.notion_type = notion_type_str
        self.options_list = None
        if self.notion_type in NOTION_SELECT_PROPERTIES:
            if options_list is not None:
                self.options_list = options_list
                if EMPTY_OPTION_DICT not in options_list:
                    self.options_list.append(EMPTY_OPTION_DICT)
        if value is not None or self.notion_type in IGNORED_PROPERTIES_SET:
            self.value = value
        else:
            if assign_default_value is True:
                self.value = self.get_default_dto_value_by_notion_type(notion_type_str)
            else:
                raise Exception("No Value provided and assign_default_value was False!")

    @property
    def html_form_type(self):
        if (
            self.notion_type in NOTION_TEXT_PROPERTIES_SET
            or self.notion_type in NOTION_SELECT_PROPERTIES
        ):
            return "text"
        if self.notion_type in NOTION_DATE_PROPERTIES_SET:
            return "datetime-local"
        if self.notion_type == "checkbox":
            return "checkbox"
        if self.notion_type == "number":
            return "number"
        return None

    @property
    def html_value(self):
        if self.notion_type == "checkbox":
            return "on" if self.value is True else "off"
        return self.value

    def dto_dict(self):
        return {
            "id": self.id,
            "type": self.notion_type,
            "value": self.value,
            "name": self.name,
            "html_form_type": self.html_form_type,
            "html_value": self.html_value,
            "options": self.options_list,
        }

    @staticmethod
    def get_default_dto_value_by_notion_type(notion_type_str):
        # Assign a default value in case of None
        if (
            notion_type_str in NOTION_TEXT_PROPERTIES_SET
            or notion_type_str in NOTION_SELECT_PROPERTIES
        ):
            return ""
        elif notion_type_str == "number":
            return 0
        elif notion_type_str in NOTION_DATE_PROPERTIES_SET:
            return now()
        elif notion_type_str == "checkbox":
            return False
        else:
            return None

    @classmethod
    def from_dto_dict(cls, dto_dict):
        return cls(
            name_str=dto_dict["name"],
            id_str=dto_dict["id"],
            notion_type_str=dto_dict["type"],
            value=dto_dict["value"],
            options_list=dto_dict["options"],
            assign_default_value=False,
        )

    @property
    def is_default_value(self):
        return self.value == self.get_default_dto_value_by_notion_type(self.notion_type)

    @classmethod
    def from_notion_api_property_dict(cls, notion_api_property_dict, property_name_str):
        property_type_str = notion_api_property_dict["type"]
        # Extract Value from the Dictionary - it is under the key of the dictionary with same value as the type
        notion_property_value = notion_api_property_dict[property_type_str]
        if property_type_str in IGNORED_PROPERTIES_SET:
            return cls(
                id_str=notion_api_property_dict["id"],
                notion_type_str=property_type_str,
                name_str=property_name_str,
                options_list=[],
                assign_default_value=False,
            )
        # check if the provided notion api returned property dict is just outlining the schema and not containg a value
        # true if the value field is showing us the available options for property or just empty dictionary
        if (
            notion_property_value == dict()
            or hasattr(notion_property_value, "__iter__")
            and "options" in notion_property_value
            or hasattr(notion_property_value, "__iter__")
            and "format" in notion_property_value
        ):
            options_list = None
            if property_type_str in NOTION_SELECT_PROPERTIES:
                options_list = notion_api_property_dict[property_type_str]["options"]
            # empty dictionary for the value means we should assign a default value
            return cls(
                id_str=notion_api_property_dict["id"],
                notion_type_str=property_type_str,
                name_str=property_name_str,
                options_list=options_list,
                assign_default_value=True,
            )

        # handle extracting the value from the property dict
        # for select properties we need to choose the currently selected value
        # Ref: https://developers.notion.com/reference/page#property-value-object
        value = None
        if property_type_str == "multi_select":
            # get the first selected attribute
            # TODO: Rework for multiple selects
            value = (
                notion_property_value[0]["id"] if len(notion_property_value) > 0 else ""
            )
        elif property_type_str == "select":
            value = notion_property_value["id"]
        elif property_type_str == "rich_text" or property_type_str == "title":
            # iterate over each text component (rich text consists of array)
            final_text_str = ""
            for text_dict in notion_property_value:
                final_text_str += text_dict["text"]["content"]
            value = final_text_str
        else:
            value = notion_property_value
        # right now, we should only have property types left where the value is assigned directly
        # in the dictionary to the key that is also the type name
        return cls(
            id_str=notion_api_property_dict["id"],
            notion_type_str=property_type_str,
            name_str=property_name_str,
            options_list=None,
            assign_default_value=False,
            value=value,
        )

    # creates a property dictionary we can use to create new properties for a page
    def get_notion_property_api_dict_for_create_page_request(self):
        if self.notion_type == "title" or self.notion_type == "rich_text":
            return [{"text": {"content": self.value}}]
        elif self.notion_type == "select":
            return {"id": self.value}
        elif self.notion_type == "multi_select":
            return [{"id": self.value}]
        else:
            return self.value
