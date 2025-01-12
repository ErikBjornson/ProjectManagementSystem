from django.urls import path, include

from .views import (
    ProjectCreateView,
    ProjectChangeStateView,
    ProjectListView,
)

project_urls = [
    path(
        route='<int:pk>/',
        view=ProjectChangeStateView.as_view(),
        name='change_project_state',
    ),
    path(
        route='list/',
        view=ProjectListView.as_view(),
        name='list_projects',
    ),
]

urls = [
    path(
        route='create',
        view=ProjectCreateView.as_view(),
        name='create_project',
    ),
] + project_urls

urlpatterns = [
    path('', include(urls)),
]
