from django.urls import path, include
from . import views


urlpatterns = [
    path("sign-up", views.sign_up_customer, name="sign-up"),
    path("sign-in", views.sign_in_customer, name="sign-in"),
    path("verify-email", views.verify_email, name="verify-email"),
    path(
        "get-customer-profile", views.get_customer_profile, name="get-customer-profile"
    ),
    path(
        "edit-customer-profile/<uuid:id>",
        views.edit_costumer_profile,
        name="edit-customer-profile",
    ),
    path(
        "delete-customer/<uuid:id>",
        views.delete_costumer,
        name="delete-customer",
    ),
    path(
        "change-costumers-password/<uuid:id>",
        views.change_constumers_password,
        name="change-costumers-password",
    ),
    path(
        "change-costumers-email/<uuid:id>",
        views.change_costumers_email,
        name="change-costumers-email",
    ),
]
