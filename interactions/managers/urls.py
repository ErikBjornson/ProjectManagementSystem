from django.urls import path, include

from staff.views import (
    ProfileView,
    ProfileChangeView,
)

urlpatterns = [
    path(
        route='profile',
        view=ProfileView.as_view(),
        name='manager_profile',
    ),
    path(
        route='profile/edit',
        view=ProfileChangeView.as_view(),
        name='manager_profile_change',
    ),
    path(
        route='projects/',
        view=include('projects.urls'),
        name='projects_work',
    ),
]
