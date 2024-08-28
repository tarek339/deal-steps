from product.controllers.products_views import *


# Create your views here.
def server(request):
    return JsonResponse({"message": "server is running..."})
