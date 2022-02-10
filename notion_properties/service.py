import notion_properties.constants as constants
from notion_properties.dto import NotionPropertyDto


def get_list_of_property_dtos_from_notion_database_resp_dict(notion_db_dict):
    property_dict_list = []
    for property_name in notion_db_dict["properties"].keys():
        notion_property_dict = notion_db_dict["properties"][property_name]
        # certain property types are not supported
        property_type_str = notion_property_dict["type"]
        if property_type_str in constants.IGNORED_PROPERTIES_SET:
            continue
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
    for property_dto in property_dto_list:
        if property_dto.is_default_value:
            continue
        create_page_property_dict[
            property_dto.name
        ] = property_dto.get_notion_property_api_dict_for_create_page_request()
    return create_page_property_dict


def is_property_dict_matching_database_schema_dict_list(
    property_dict, db_schema_property_dict_list
):
    if "type" not in property_dict:
        return False
    property_type = property_dict["type"]
    matching_db_schema_property_dict = None
    for db_property_dict in db_schema_property_dict_list:
        if (
            db_property_dict["type"] == property_type
            and db_property_dict["id"] == property_dict["id"]
        ):
            matching_db_schema_property_dict = property_dict
            break
    if matching_db_schema_property_dict is None:
        return False
    property_value = property_dict["value"]
    if type in constants.NOTION_SELECT_PROPERTIES:
        for option in matching_db_schema_property_dict["options"]:
            if option == property_value:
                return True
        return False
    elif type == "number":
        try:
            value_as_number = int(property_value)
        except ValueError:
            try:
                value_as_number = float(property_value)
                return True
            except ValueError:
                return False
    else:
        return True
