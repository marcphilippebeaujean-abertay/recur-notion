from notion_embeds.models import NotionEmbedPropertySettings


def create_notion_property_settings_from_notion_database_and_embed_model(
    notion_embed_model, notion_database_model
):
    notion_property_settings = []
    for notion_property_meta_data in notion_database_model.notion_properties.all():
        (
            notion_embed_property_setting,
            created,
        ) = NotionEmbedPropertySettings.objects.get_or_create(
            property=notion_property_meta_data, database_embed=notion_embed_model
        )
        notion_property_settings.append(notion_embed_property_setting)
    return notion_property_settings
