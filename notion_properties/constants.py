NOTION_DATE_PROPERTIES_SET = {"last_edited_time", "created_time", "date"}
IGNORED_PROPERTIES_SET = set.union(
    {
        "relation",
        "formula",
        "rollup",
        "created_time",
        "created_by",
        "last_edited_time",
        "last_edited_by",
        "people",
        "files",
    },
    NOTION_DATE_PROPERTIES_SET,
)
NOTION_TEXT_PROPERTIES_SET = {"email", "phone_number", "rich_text", "title", "url"}
NOTION_SELECT_PROPERTIES = {"multi_select", "select"}
EMPTY_OPTION_DICT = {"id": "", "name": ""}
