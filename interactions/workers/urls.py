from django.urls import path

from staff.views import (
    ProfileView,
    ProfileChangeView,
)

urlpatterns = [
    path(
        route='profile',
        view=ProfileView.as_view(),
        name='worker_profile',
    ),
    path(
        route='profile/edit',
        view=ProfileChangeView.as_view(),
        name='worker_profile_change',
    ),
]
