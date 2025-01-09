from django.urls import path

from .views import (
    RegistrationView,
    VerificationOfRegistrationView,
    LoginView,
    RefreshView,
    PasswordRecoveryView,
    PasswordRecoveryVerifyView,
    PasswordRecoveryChangeView,
)

urlpatterns = [
    path(
        route='register',
        view=RegistrationView.as_view(),
        name='register',
    ),
    path(
        route='activate',
        view=VerificationOfRegistrationView.as_view(),
        name='activate',
    ),
    path(
        route='login',
        view=LoginView.as_view(),
        name='login',
    ),
    path(
        route='refresh',
        view=RefreshView.as_view(),
        name='refresh',
    ),
    path(
        route='password-recovery',
        view=PasswordRecoveryView.as_view(),
        name='password_recovery',
    ),
    path(
        route='password-recovery/verify',
        view=PasswordRecoveryVerifyView.as_view(),
        name='password_recovery_verify',
    ),
    path(
        route='password-recovery/change',
        view=PasswordRecoveryChangeView.as_view(),
        name='password_recovery_change',
    ),
]
