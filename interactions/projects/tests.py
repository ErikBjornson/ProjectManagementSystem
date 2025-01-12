from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APITestCase,
    APIRequestFactory,
    force_authenticate,
)

from .models import Project

from .views import (
    ProjectListView,
    ProjectCreateView,
    ProjectChangeStateView,
)

from staff.models import Employee


class CreateProjectTests(APITestCase):
    """Тестирование процесса создания проекта."""

    def setUp(self):
        self.factory = APIRequestFactory()

        self.admin_user = Employee.objects.create_user(
            email='admin_user@test.ru',
            password='12345678',
            user_type='admin',
        )
        self.worker_user = Employee.objects.create_user(
            email='worker_user@test.ru',
            password='87654321',
            user_type='worker',
        )
        self.view = ProjectCreateView.as_view()

    def test_successfull_creating(self):
        request = self.factory.post(
            path=reverse('create_project'),
            data={
                'admin_id': self.admin_user.pk,
                'title': 'first_project',
                'description': 'first project description',
            },
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

    def test_project_with_title_already_exists(self):
        first_request = self.factory.post(
            path=reverse('create_project'),
            data={
                'admin_id': self.admin_user.pk,
                'title': 'new_project',
                'description': 'first project description',
            },
            format='json',
        )
        force_authenticate(request=first_request, user=self.admin_user)
        self.view(first_request)

        request = self.factory.post(
            path=reverse('create_project'),
            data={
                'admin_id': self.admin_user.pk,
                'title': 'new_project',
                'description': 'second project description',
            },
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Project with this title already exists!",
            response.data.get('title'),
        )

    def test_project_creator_not_admin(self):
        request = self.factory.post(
            path=reverse('create_project'),
            data={
                'admin_id': self.worker_user.pk,
                'title': 'my_project',
                'description': 'first project description',
            },
            format='json',
        )
        force_authenticate(request=request, user=self.worker_user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Only users with user_type='admin' can create projects!",
            response.data.get('admin_id'),
        )

    def test_missing_parameters(self):
        request = self.factory.post(
            path=reverse('create_project'),
            data={
                'admin_id': self.admin_user.pk,
                'title': 'my_new_project',
            },
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This field is required.",
            response.data.get('description'),
        )

    def test_blank_field(self):
        request = self.factory.post(
            path=reverse('create_project'),
            data={
                'admin_id': self.admin_user.pk,
                'title': '',
                'description': 'first project description',
            },
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This field may not be blank.",
            response.data.get('title'),
        )


class ChangeStateProjectTests(APITestCase):
    """Тестирование процесса изменения/получения данных/удаления проекта."""

    def setUp(self):
        self.factory = APIRequestFactory()

        self.admin_user = Employee.objects.create(
            email='admin_user@test.ru',
            password='12345678',
            user_type='admin',
        )
        self.worker_user = Employee.objects.create_user(
            email='worker_user@test.ru',
            password='87654321',
            user_type='worker',
        )

        self.project = Project.objects.create(
            admin_id=self.admin_user.pk,
            title='change_state_tests_project',
            description='change state tests project description',
        )

        self.url = reverse(
            'change_project_state',
            kwargs={'pk': self.project.pk},
        )
        self.view = ProjectChangeStateView.as_view()
        self.create_view = ProjectCreateView.as_view()

    def test_successfull_delete_project(self):
        request = self.factory.delete(
            path=self.url,
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request, pk=self.project.pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_successfull_get_project_data(self):
        request = self.factory.get(
            path=self.url,
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request, pk=self.project.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.project.pk, response.data.get('id'))
        self.assertEqual(self.admin_user.pk, response.data.get('admin_id'))
        self.assertTrue(isinstance(response.data, dict))

    def test_successfull_change_project_data(self):
        request = self.factory.patch(
            path=self.url,
            data={
                'description': 'new description',
            },
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request, pk=self.project.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('description'), 'new description')

    def test_incorrect_blank_change_project_data(self):
        request = self.factory.patch(
            path=self.url,
            data={
                'description': '',
            },
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request, pk=self.project.pk)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This field may not be blank.",
            response.data.get('description'),
        )

    def test_incorrect_creator_change_project_data(self):
        request = self.factory.patch(
            path=self.url,
            data={
                'admin_id': self.worker_user.pk,
            },
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request, pk=self.project.pk)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Only users with user_type='admin' can create projects!",
            response.data.get('admin_id'),
        )

    def test_incorrect_title_change_project_data(self):
        first_request = self.factory.post(
            path=reverse('create_project'),
            data={
                'admin_id': self.admin_user.pk,
                'title': 'PROJECT',
                'description': 'tests PROJECT description',
            }
        )
        force_authenticate(request=first_request, user=self.admin_user)
        self.create_view(first_request)

        request = self.factory.patch(
            path=self.url,
            data={
                'title': 'PROJECT',
            },
            format='json',
        )
        force_authenticate(request=request, user=self.admin_user)
        response = self.view(request, pk=self.project.pk)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Project with this title already exists!",
            response.data.get('title'),
        )


class ProjectsListTests(APITestCase):
    """Тестирование процесса получения списка проектов."""

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = Employee.objects.create_user(
            email='admin_user@test.ru',
            password='12345678',
            user_type='admin',
        )

        Project.objects.create(
            admin_id=self.user.pk,
            title='projects_list_check_project',
            description='test description',
        )

        self.view = ProjectListView.as_view()

    def test_get_projects_list(self):
        request = self.factory.get(
            path=reverse('list_projects'),
            format='json',
        )
        force_authenticate(request=request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
