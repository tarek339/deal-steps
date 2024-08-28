from product.lib.index import *
from django.http import JsonResponse
import json
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from customer.models import *
from ..models import *


def update_products():
    # delete_from_database(Product)
    zalando = scrape_products(
        "https://www.zalando.de/schuhe/",
        "Zalando",
        "article",
        "z5x6ht _0xLoFW JT3_zV mo6ZnF _78xIQ-",
        "h3",
        "FtrEr_ lystZ1 FxZV-M HlZ_Tf ZkIJC- r9BRio qXofat EKabf7",
        "h3",
        "sDq_FX lystZ1 FxZV-M HlZ_Tf ZkIJC- r9BRio qXofat EKabf7",
        "p",
        ["sDq_FX lystZ1 dgII7d HlZ_Tf", "sDq_FX lystZ1 FxZV-M HlZ_Tf"],
    )
    # deichmann_sale = scrape_products(
    #     "https://www.deichmann.com/de-de/herren-schuhe/sneaker/c-mss3",
    #     "Deichmann",
    #     "article",
    #     "m-product-card-entry",
    #     "h4",
    #     "",
    #     "h3",
    #     "",
    #     "strong",
    #     "sale",
    # )
    # deichmann = scrape_products(
    #     "https://www.deichmann.com/de-de/herren-schuhe/sneaker/c-mss3",
    #     "Deichmann",
    #     "article",
    #     "m-product-card-entry",
    #     "h4",
    #     "",
    #     "h3",
    #     "",
    #     "strong",
    #     "",
    # )
    # about_you = scrape_products(
    #     "https://www.aboutyou.de/b/shop/nike-272/all?category=20345&sale=true",
    #     "About You",
    #     "li",
    #     "sc-oelsaz-0 YkKBp",
    #     "p",
    #     "sc-1vt6vwe-0 sc-1vt6vwe-1 sc-1qsfqrd-3 jQLlAg uXZUf iBzidq",
    #     "p",
    #     "sc-1vt6vwe-0 sc-1vt6vwe-1 sc-1qsfqrd-4 jQLlAg uXZUf KJYZl",
    #     "span",
    #     "sc-2qclq4-0 sc-fruv23-0 llOhHy fzbBtI sc-18q4lz4-0 jqbzko",
    # )
    store_in_database(zalando)
    # store_in_database(deichmann_sale)
    # store_in_database(deichmann)
    # store_in_database(about_you)


# update_products()


@csrf_exempt
def fetch_products(request):
    if request.method == "GET":
        products = Product.objects.values()
        return JsonResponse(
            list(products),
            safe=False,
            status=status.HTTP_200_OK,
        )

    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def fetch_single_product(request, productID):
    if request.method == "GET":
        product = Product.objects.get(id=productID)
        if product:
            data = {
                "id": product.id,
                "shopName": product.shopName,
                "brand": product.brand,
                "description": product.description,
                "price": product.price,
                "imageUrl": product.imageUrl,
            }
            return JsonResponse(
                data,
                status=status.HTTP_200_OK,
            )
    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def add_to_cart(request, id):
    if request.method == "POST":
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        product_id = body_data.get("productId")
        customer_id = get_object_or_404(Customer, id=id)
        product = get_object_or_404(Product, id=product_id)

        cart, created = Cart.objects.get_or_create(customer=customer_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            cart_item.quantity = 1
        else:
            cart_item.quantity += 1
        cart_item.save()

        return JsonResponse(
            {"message": "Item added to cart"},
            status=status.HTTP_200_OK,
        )

    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def fetch_cart(request, id):
    if request.method == "GET":
        customer_id = get_object_or_404(Customer, id=id)

        try:
            cart = Cart.objects.get(customer=customer_id)

            cart_data = []
            total_sum = 0

            for item in cart.items.all():
                item_total_price = item.total
                cart_data.append(
                    {
                        "id": item.product.id,
                        "brand": item.product.brand,
                        "quantity": item.quantity,
                        "totalPrice": item.total,
                    }
                )
                total_sum += item_total_price

            return JsonResponse(
                {"cart": cart_data, "total": total_sum}, status=status.HTTP_200_OK
            )
        except:
            return JsonResponse(
                {"message": "Cart is empty"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def remove_from_cart(request, id):
    if request.method == "POST":
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        product_id = body_data.get("productId")
        customer_id = get_object_or_404(Customer, id=id)
        product = get_object_or_404(Product, id=product_id)

        cart = Cart.objects.get(customer=customer_id)
        cart_item = CartItem.objects.get(cart=cart, product=product)

        if cart_item.quantity > 0:
            cart_item.quantity -= 1
            cart_item.save()

        if cart_item.quantity <= 0:
            cart_item.delete()

        return JsonResponse({"message": "Item removed from cart"})

    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def delete_cart(request, id):
    if request.method == "POST":
        customer_id = get_object_or_404(Customer, id=id)

        cart = Cart.objects.get(customer=customer_id)
        cart_items = CartItem.objects.filter(cart=cart)

        for item in cart_items:
            item.delete()

        return JsonResponse({"message": "Cart deleted"})

    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
