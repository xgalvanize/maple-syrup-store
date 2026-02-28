from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from syrupstore.schema import schema
from shop.views import download_receipt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True))),
    path("api/receipts/download/<int:order_id>/", download_receipt, name="download_receipt"),
]
