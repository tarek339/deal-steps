import json
from ..models import *
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from customer.middlewares.with_sign_in import with_sign_in
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import jwt
import datetime


@csrf_exempt
def sign_up_customer(request):
    if request.method == "POST":
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        email = body_data.get("email")
        password = body_data.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Customer.objects.filter(email=email).exists():
            return JsonResponse(
                {"error": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_customer = Customer()

        # Generate email confirmation token
        emailToken = default_token_generator.make_token(new_customer)
        uid = urlsafe_base64_encode(force_bytes(new_customer.pk))

        # Send verification email
        verification_link = (
            f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={emailToken}"
        )
        new_customer = Customer(
            email=email,
            password=password,
            verificationToken=emailToken,
        )
        new_customer.save()

        send_mail(
            "Verify Your Email",
            f"Hi, please verify your email by clicking on the link: {verification_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Generate token for locale storage
        expiration_time = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(days=7)

        token = jwt.encode(
            {"exp": expiration_time, "user_id": str(new_customer.id)},
            settings.JWT_SECRET,
            algorithm="HS256",
        )

        return JsonResponse(
            {
                "user": {
                    "email": email,
                },
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )
    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        verificationToken = body_data.get("token")

        customer = Customer.objects.get(verificationToken=verificationToken)

        if customer:
            customer.isVerified = True
            customer.save()
        else:
            return JsonResponse(
                {"error": "Invalid token."},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        return JsonResponse(
            {
                "message": "new costumer verified",
                "customer": {
                    "id": customer.id,
                    "firstName": customer.firstName,
                    "lastName": customer.lastName,
                    "email": customer.email,
                    "street": customer.street,
                    "houseNumber": customer.houseNumber,
                    "zipCode": customer.zipCode,
                    "city": customer.city,
                    "isVerified": customer.isVerified,
                },
            },
            status=status.HTTP_202_ACCEPTED,
        )

    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def sign_in_customer(request):
    if request.method == "POST":
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        email = body_data.get("email")
        password = body_data.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            customer = Customer.objects.get(email=email)
            checked = customer.check_password(password)
            if checked and customer.email is not None:
                # Generate token for locale storage
                expiration_time = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(days=7)

                token = jwt.encode(
                    {"exp": expiration_time, "user_id": str(customer.id)},
                    settings.JWT_SECRET,
                    algorithm="HS256",
                )
                return JsonResponse(
                    {
                        "message": "Login successful",
                        "user": {
                            "id": customer.id,
                            "firstName": customer.firstName,
                            "lastName": customer.lastName,
                            "email": customer.email,
                            "street": customer.street,
                            "houseNumber": customer.houseNumber,
                            "zipCode": customer.zipCode,
                            "city": customer.city,
                            "isVerified": customer.isVerified,
                        },
                        "token": token,
                    },
                    status=status.HTTP_200_OK,
                )
            return JsonResponse(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        except Customer.DoesNotExist:
            return JsonResponse(
                {"message": "Customer with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    else:
        return JsonResponse(
            {"error": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def get_customer_profile(request):
    if request.method == "GET":
        customer_id = with_sign_in(request)

        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            return JsonResponse(
                {
                    "user": {
                        "id": customer.id,
                        "firstName": customer.firstName,
                        "lastName": customer.lastName,
                        "email": customer.email,
                        "street": customer.street,
                        "houseNumber": customer.houseNumber,
                        "zipCode": customer.zipCode,
                        "city": customer.city,
                        "isVerified": customer.isVerified,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return JsonResponse(
                {"error": "No user signed in"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

    else:
        return JsonResponse(
            {"error": "not authorized"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


@csrf_exempt
def edit_costumer_profile(request, id):
    if request.method == "PUT":
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        firstName = body_data.get("firstName")
        lastName = body_data.get("lastName")
        street = body_data.get("street")
        houseNumber = body_data.get("houseNumber")
        zipCode = body_data.get("zipCode")
        city = body_data.get("city")

        try:
            customer = Customer.objects.get(id=id)
            customer.firstName = firstName
            customer.lastName = lastName
            customer.street = street
            customer.houseNumber = houseNumber
            customer.zipCode = zipCode
            customer.city = city
            customer.save()

        except Customer.DoesNotExist:
            return JsonResponse(
                {"message": "Customer with this ID does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return JsonResponse(
            {
                "message": "profile successfully edited",
                "user": {
                    "id": customer.id,
                    "firstName": customer.firstName,
                    "lastName": customer.lastName,
                    "email": customer.email,
                    "street": customer.street,
                    "houseNumber": customer.houseNumber,
                    "zipCode": customer.zipCode,
                    "city": customer.city,
                    "isVerified": customer.isVerified,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    else:
        return JsonResponse(
            {"error": "not authorized"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


@csrf_exempt
def change_constumers_password(request, id):
    try:
        request.method == "PUT"
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        old_password = body_data.get("oldPassword")
        new_password = body_data.get("newPassword")
        confirm_new_password = body_data.get("confirmPassword")

        if not old_password:
            return JsonResponse(
                {"message": "Password is required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        customer = Customer.objects.get(id=id)
        checked = customer.check_password(old_password)

        if checked:
            if new_password == confirm_new_password:
                customer.password = new_password
                customer.save()
                return JsonResponse(
                    {"message": "Passwords successfully changed"},
                    status=status.HTTP_201_CREATED,
                )

            return JsonResponse(
                {"message": "Passwords must match"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return JsonResponse(
            {"message": "Password is incorrect"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    except request.HTTP_405_METHOD_NOT_ALLOWED:
        return JsonResponse(
            {"error": "not authorized"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


@csrf_exempt
def change_costumers_email(request, id):
    if request.method == "PUT":
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)
        new_email = body_data.get("newEmail")
        confirm_email = body_data.get("confirmEmail")

        if not new_email:
            return JsonResponse(
                {"message": "Email is required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            customer = Customer.objects.get(id=id)

            if new_email == confirm_email:
                if customer:
                    emailToken = default_token_generator.make_token(customer)
                    uid = urlsafe_base64_encode(force_bytes(customer.pk))

                    customer.isVerified = False
                    customer.verificationToken = emailToken
                    customer.email = new_email
                    customer.save()

                    verification_link = f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={emailToken}"

                    send_mail(
                        "Verify Your Email",
                        f"Hi, please verify your email by clicking on the link: {verification_link}",
                        settings.DEFAULT_FROM_EMAIL,
                        [new_email],
                        fail_silently=False,
                    )
                return JsonResponse(
                    {"message": "Check your inbox to verify the new email"},
                    status=status.HTTP_200_OK,
                )
            return JsonResponse(
                {"message": "E-Mails must match"},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        except Customer.DoesNotExist:
            return JsonResponse(
                {"message": "Customer with this ID does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    else:
        return JsonResponse(
            {"error": "not authorized"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


@csrf_exempt
def delete_costumer(request, id):
    if request.method == "DELETE":
        customer = get_object_or_404(Customer, id=id)
        customer.delete()

        return JsonResponse(
            {"message": "profile deleted"}, status=status.HTTP_204_NO_CONTENT
        )

    else:
        return JsonResponse(
            {"error": "not authorized"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
