from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)

from .models import Project

from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
)

from staff.authentication import (
    EmployeeJWTAuthentication,
    IsAuthenticatedEmployee,
)


class ProjectCreateView(CreateAPIView):
    """View создания проекта."""

    queryset = Project.objects.all()
    serializer_class = ProjectCreateSerializer
    permission_classes = [IsAuthenticatedEmployee]
    authentication_classes = [EmployeeJWTAuthentication]


class ProjectChangeStateView(RetrieveUpdateDestroyAPIView):
    """View изменения и удаления проекта и получения информации о нём."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedEmployee]
    authentication_classes = [EmployeeJWTAuthentication]


class ProjectListView(ListAPIView):
    """View вывода списка проектов."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedEmployee]
    authentication_classes = [EmployeeJWTAuthentication]
