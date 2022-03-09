import notion_properties.constants as constants
from notion_properties.dto import NotionPropertyDto


def get_list_of_property_dtos_from_notion_database_resp_dict(notion_db_dict):
    property_dict_list = []
    for property_name in notion_db_dict["properties"].keys():
        notion_property_dict = notion_db_dict["properties"][property_name]
        # certain property types are not supported
        property_dict_list.append(
            NotionPropertyDto.from_notion_api_property_dict(
                notion_property_dict, property_name
            )
        )
    return property_dict_list


def create_properties_dict_for_create_page_api_request_from_property_dto_list(
    property_dto_list,
):
    create_page_property_dict = {}
    # don't include properties where values are default i.e. not set, with exception of checkbox
    for property_dto in property_dto_list:
        if property_dto.is_default_value and property_dto.notion_type != "checkbox":
            continue
        create_page_property_dict[
            property_dto.name
        ] = property_dto.get_notion_property_api_dict_for_create_page_request()
    return create_page_property_dict


def get_list_of_premium_property_names_in_notion_property_dto_list(property_dto_list):
    ignored_property_name_list = []
    for property_dto in property_dto_list:
        if property_dto.notion_type in constants.PREMIUM_PROPERTIES_SET:
            ignored_property_name_list.append(property_dto.name)
    return ignored_property_name_list
