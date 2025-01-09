from smtplib import SMTPException

from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Employee

from .serializers import (
    RegistrationSerializer,
    RegistrationVerifySerializer,
    LoginSerializer,
    PasswordRecoverySerializer,
    PasswordRecoveryVerifySerializer,
    PasswordRecoveryChangeSerializer,
    ProfileSerializer,
    ProfileChangeSerializer,
)

from .authentication import (
    EmployeeJWTAuthentication,
    IsAuthenticatedEmployee,
)

from interactions.verification import (
    RegistrationCache,
    make_verification_code,
    send_verification_code,
    PasswordRecoveryCache,
)


class RegistrationView(APIView):
    """View регистрации сотрудника."""

    def post(self, request) -> Response:
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        verification_code = make_verification_code()

        RegistrationCache.save(
            email=email,
            code=verification_code,
            data=serializer.validated_data,
        )

        try:
            send_verification_code(
                email=email,
                verification_code=verification_code,
            )
        except SMTPException:
            return Response(
                {'message': 'Email not found!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {'message': "You've successfully registered!"},
            status=status.HTTP_200_OK,
        )


class VerificationOfRegistrationView(APIView):
    """View верификации регистрации сотрудника."""

    def post(self, request) -> Response:
        serializer = RegistrationVerifySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        verification_code = serializer.validated_data['verification_code']

        data = RegistrationCache.verify(email=email, code=verification_code)

        if not data:
            return Response(
                {'message': 'Incorrect verification code!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RegistrationSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'message': "You've successfully registered!"},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    """View авторизации сотрудника."""

    def post(self, request) -> Response:
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request=request, email=email, password=password)

        if user:
            refresh_token = RefreshToken.for_user(user)

            refresh_token.payload.update({'user_id': user.id})

            return Response(
                {
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {'password': 'Incorrect password!'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RefreshView(APIView):
    """View получения refresh-токена."""

    def post(self, request) -> Response:
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response(
                {'refresh': 'refresh - this field is required!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh_token = RefreshToken(refresh_token)
            return Response(
                {'access': str(refresh_token.access_token)},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {'refresh': 'refresh code is not active!'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordRecoveryView(APIView):
    """VIew восстановления пароля сотрудника."""

    def post(self, request) -> Response:
        serializer = PasswordRecoverySerializer(data=request.data)

        if serializer.is_valid():
            verification_code = make_verification_code()
            email = serializer.validated_data['email']

            PasswordRecoveryCache.save(
                email=email,
                code=verification_code,
            )

            try:
                send_verification_code(
                    email=email,
                    verification_code=verification_code,
                )
                return Response(
                    {'message': 'Check your email for the verification_code.'},
                    status=status.HTTP_200_OK,
                )
            except SMTPException:
                return Response(
                    {'email': ['The email not found.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordRecoveryVerifyView(APIView):
    """View верификации при восстановлении пароля сотрудника."""

    def post(self, request) -> Response:
        serializer = PasswordRecoveryVerifySerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            verify_code = serializer.validated_data['verification_code']

            if PasswordRecoveryCache.verify(email=email, code=verify_code):
                return Response(
                    {'message': ['Verification was successful.']},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    'verification_code':
                        ['The verification code is not active.'],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordRecoveryChangeView(APIView):
    """View смены пароля сотрудника."""

    def post(self, request) -> Response:
        serializer = PasswordRecoveryChangeSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            if PasswordRecoveryCache.check(email=email):
                serializer.save()
                return Response(
                    {'message': ['Password successfully changed.']},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {'email': ['Something went wrong.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProfileView(RetrieveAPIView):
    """View получения данных профиля сотрудника."""

    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticatedEmployee]
    authentication_classes = [EmployeeJWTAuthentication]

    def retrieve(self, request, *args, **kwargs):
        serializer = ProfileSerializer(self.request.user)
        return Response(serializer.data)


class ProfileChangeView(UpdateAPIView):
    """View изменения данных профиля сотрудника."""

    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticatedEmployee]
    authentication_classes = [EmployeeJWTAuthentication]

    def update(self, request, *args, **kwargs):
        serializer = ProfileChangeSerializer(
            self.request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
