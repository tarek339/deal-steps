from django.contrib import admin
from django.urls import path, include
import debug_toolbar


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("product.urls")),
    path("product/", include("product.urls")),
    path("customer/", include("customer.urls")),
    path("__debug__", include(debug_toolbar.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
