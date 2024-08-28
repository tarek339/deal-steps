from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.server, name="server"),
    path("fetch-products", views.fetch_products, name="fetch-products"),
    path(
        "fetch-single-product/<uuid:productID>",
        views.fetch_single_product,
        name="fetch-single-product",
    ),
    path("add-to-cart/<uuid:id>", views.add_to_cart, name="add-to-cart"),
    path("fetch-cart/<uuid:id>", views.fetch_cart, name="fetch-cart"),
    path("remove-from-cart/<uuid:id>", views.remove_from_cart, name="remove-from-cart"),
    path("delete-cart/<uuid:id>", views.delete_cart, name="delete-cart"),
]
