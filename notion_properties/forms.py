from crispy_forms.bootstrap import Alert, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Row, Submit
from django import forms
from django.urls import reverse

from notion_properties.constants import (
    IGNORED_PROPERTIES_SET,
    NOTION_SELECT_PROPERTIES,
    NOTION_TEXT_PROPERTIES_SET,
)
from notion_properties.dto import NotionPropertyDto
from notion_properties.template_tags import icon_by_property_type
from pages.template_tags import bootstrap_icon_by_icon_name


class NotionPropertyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        task_model = kwargs.pop("task_model")
        show_save_notification = False
        if "show_save_notification" in kwargs:
            show_save_notification = kwargs.pop("show_save_notification")

        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_action = reverse(
            "update-recurring-task-properties", kwargs={"pk": task_model.pk}
        )
        self.helper.form_method = "POST"

        properties_dict_list = task_model.properties_json
        if isinstance(properties_dict_list, list) is False:
            return
        properties_dto_list = [
            NotionPropertyDto.from_dto_dict(property_dict)
            for property_dict in properties_dict_list
        ]
        properties_dto_list = [
            property_dto
            for property_dto in properties_dto_list
            if property_dto.notion_type != "title"
            and property_dto.notion_type not in IGNORED_PROPERTIES_SET
        ]

        notion_property_dto_by_id = {}
        for i, property_dto in enumerate(properties_dto_list):
            field_name = property_dto.id
            if property_dto.notion_type in NOTION_SELECT_PROPERTIES:
                self.fields[field_name] = forms.ChoiceField(
                    required=False,
                    choices=[
                        (option["id"], option["name"])
                        for option in property_dto.options_list
                    ],
                )
            elif property_dto.notion_type == "checkbox":
                self.fields[field_name] = forms.BooleanField(required=False)
            elif property_dto.notion_type == "number":
                self.fields[field_name] = forms.DecimalField(required=False)
            elif property_dto.notion_type in NOTION_TEXT_PROPERTIES_SET:
                self.fields[field_name] = forms.CharField(required=False)
            else:
                raise Exception("Unexpected Notion property type for Form!")
            self.fields[field_name].initial = property_dto.value
            self.fields[field_name].label = property_dto.name

            notion_property_dto_by_id[field_name] = property_dto

        unsupported_properties_alert = None
        if (
            task_model.database is not None
            and len(task_model.database.get_list_of_unsupported_property_names()) > 0
        ):
            alert_message = f'{bootstrap_icon_by_icon_name(icon_name="info-circle")} '
            alert_message += "The following properties are currently not supported (but will be in future updates): "
            alert_message += ", ".join(
                task_model.database.get_list_of_unsupported_property_names()
            )
            unsupported_properties_alert = Alert(
                content=alert_message,
                css_class="hide-internal-buttons alert-warning mt-2 mb-0",
            )

        submit_btn = HTML(
            """
            <button type="submit"
                class="btn btn-success mt-2"
                x-bind:disabled="loading || !changed">
                <span class="spinner-border spinner-border-sm"
                  role="status"
                  aria-hidden="true"
                  x-show="loading"></span>
                &nbsp;Save Properties
            </button>'
        """
        )

        saved_notification_text = (
            ""
            if show_save_notification is False
            else f'<span class="text-success">{bootstrap_icon_by_icon_name(icon_name="check-circle-fill")}</span> '
            f'<span class="text-dark">Changes Saved!</span>'
        )

        self.helper.layout = Layout(
            Div(
                *[
                    PrependedText(
                        field,
                        ""
                        if notion_property_dto_by_id[field].notion_type == "checkbox"
                        else icon_by_property_type(
                            notion_property_dto_by_id[field].notion_type
                        ),
                        wrapper_class="col-md-6 mt-1",
                        css_class="properties-input",
                        **{"@keyup": "changed=true", "@change": "changed=true"},
                    )
                    for field in self.fields
                ],
                css_class="d-flex row",
            ),
            unsupported_properties_alert,
            submit_btn,
            HTML(
                f'<p class="text-muted mt-2 mb-0" x-show="!changed">{saved_notification_text} No Unsaved Changes.</p>'
            ),
        )
