from django.urls import path

urlpatterns = [
    path(
        route='register',
    ),
    path(
        route='login',
    ),
    path(
        route='password-recovery',
    ),
    path(
        route='password-recovery/verify',
    ),
    path(
        route='password-recovery/change',
    ),
    path(
        route='profile',
    ),
]
