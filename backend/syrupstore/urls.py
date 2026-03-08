from django.contrib import admin
from django.urls import path, include
from syrupstore.schema import schema
from syrupstore.views import RateLimitedGraphQLView, health_check
from shop.views import download_receipt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", RateLimitedGraphQLView.as_view(schema=schema, graphiql=True)),
    path("api/receipts/download/<int:order_id>/", download_receipt, name="download_receipt"),
    path("health/", include("health_check.urls")),
    path("api/health/", health_check, name="health_check"),
]
