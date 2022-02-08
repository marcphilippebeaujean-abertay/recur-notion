from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("n1L53rWNOLDDLA9q/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
    path("", include("workspaces.urls")),
    path("", include("tasks.urls")),
    path("", include("notion_database.urls")),
    path("", include("newsletter.urls")),
    path("wagtail/Ph5LX3aK", include(wagtailadmin_urls)),
    path("wagtail/documents/", include(wagtaildocs_urls)),
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's serving mechanism
    re_path(r"", include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
