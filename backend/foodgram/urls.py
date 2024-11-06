from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API foodgram_project",
        default_version="v1",
        description="foodgram_project backend",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls", namespace="api")),
    url(r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
        ),
    url(r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
        ),
    url(r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc"
        ),
] + static(settings.STATIC_URL,
           document_root=settings.STATIC_ROOT
           )
