from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("n1L53rWNOLDDLA9q/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
    path("", include("workspaces.urls")),
    path("", include("notion_embeds.urls")),
    path("", include("notion_database.urls")),
    path("", include("newsletter.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
