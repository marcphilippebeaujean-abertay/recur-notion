import urllib

from django import template

from config.settings import NOTION_OAUTH_CALLBACK, NOTION_CLIENT_ID
import urllib.parse

register = template.Library()


@register.simple_tag
def oauth_url():
    callback_url = urllib.parse.quote(NOTION_OAUTH_CALLBACK)
    return f'https://api.notion.com/v1/oauth/authorize?owner=user&client_id={NOTION_CLIENT_ID}&redirect_uri={callback_url}&response_type=code'
