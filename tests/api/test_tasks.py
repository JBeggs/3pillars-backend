"""
Tests for Tasks API endpoints.
"""
from django.test import tag
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Task, Project, TaskStage, ProjectStage
from tests.base_test_classes import BaseTestCase

User = get_user_model()


@tag('APITest')
class TaskAPITestCase(BaseTestCase, APITestCase):
    """Test Task API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_active=True
        )
        cls.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            email='other@example.com',
            is_active=True
        )
        cls.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        
        # Get default task stage
        task_stage = TaskStage.objects.filter(default=True).first()
        if not task_stage:
            task_stage = TaskStage.objects.first()
        
        cls.task = Task.objects.create(
            name='Test Task',
            description='Test description',
            stage=task_stage,
            owner=cls.user,
            active=True
        )
        cls.task.responsible.add(cls.user)
        
        cls.other_task = Task.objects.create(
            name='Other Task',
            stage=task_stage,
            owner=cls.other_user,
            active=True
        )
    
    def setUp(self):
        print(f"Run Test Method: {self._testMethodName}")
        self.client.force_authenticate(user=self.user)
    
    def test_list_tasks(self):
        """Test listing tasks."""
        url = '/api/tasks/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_tasks_assigned_to_me(self):
        """Test filtering tasks assigned to me."""
        url = '/api/tasks/?assigned_to_me=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        # Should only see tasks where user is responsible
        for task in results:
            self.assertIn(self.user.id, task.get('responsible', []))
    
    def test_list_tasks_created_by_me(self):
        """Test filtering tasks created by me."""
        url = '/api/tasks/?created_by_me=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        # Should only see tasks created by user
        for task in results:
            self.assertEqual(task['owner'], self.user.id)
    
    def test_create_task(self):
        """Test creating a task."""
        from datetime import date, timedelta
        
        # Get default task stage
        task_stage = TaskStage.objects.filter(default=True).first()
        if not task_stage:
            task_stage = TaskStage.objects.first()
        
        url = '/api/tasks/'
        data = {
            'name': 'New Task',
            'description': 'Task description',
            'note': 'Task note',
            'priority': 1,
            'stage': task_stage.id if task_stage else None,
            'next_step': 'Initial task setup',
            'next_step_date': (date.today() + timedelta(days=7)).isoformat(),
            'active': True,
            'responsible': [self.user.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Task')
        self.assertEqual(response.data['owner'], self.user.id)
        self.assertIn(self.user.id, response.data.get('responsible', []))
    
    def test_create_task_auto_sets_owner(self):
        """Test that creating task automatically sets owner."""
        from datetime import date, timedelta
        
        # Get default task stage
        task_stage = TaskStage.objects.filter(default=True).first()
        if not task_stage:
            task_stage = TaskStage.objects.first()
        
        url = '/api/tasks/'
        data = {
            'name': 'Auto Owner Task',
            'stage': task_stage.id if task_stage else None,
            'next_step': 'Initial setup',
            'next_step_date': (date.today() + timedelta(days=7)).isoformat(),
            'active': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.user.id)
    
    def test_create_task_with_multiple_responsible(self):
        """Test creating task with multiple responsible users."""
        from datetime import date, timedelta
        
        # Get default task stage
        task_stage = TaskStage.objects.filter(default=True).first()
        if not task_stage:
            task_stage = TaskStage.objects.first()
        
        url = '/api/tasks/'
        data = {
            'name': 'Multi User Task',
            'stage': task_stage.id if task_stage else None,
            'next_step': 'Assign to team',
            'next_step_date': (date.today() + timedelta(days=7)).isoformat(),
            'active': True,
            'responsible': [self.user.id, self.other_user.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        responsible_ids = response.data.get('responsible', [])
        self.assertIn(self.user.id, responsible_ids)
        self.assertIn(self.other_user.id, responsible_ids)
    
    def test_get_task_detail(self):
        """Test retrieving task detail."""
        url = f'/api/tasks/{self.task.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.task.id)
        self.assertEqual(response.data['name'], 'Test Task')
    
    def test_update_task(self):
        """Test updating a task."""
        url = f'/api/tasks/{self.task.id}/'
        data = {'name': 'Updated Task Name'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Task Name')
    
    def test_mark_task_complete(self):
        """Test marking task as complete."""
        done_stage = TaskStage.objects.filter(done=True).first()
        if done_stage:
            url = f'/api/tasks/{self.task.id}/mark_complete/'
            response = self.client.post(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.task.refresh_from_db()
            self.assertEqual(self.task.stage.id, done_stage.id)
            self.assertFalse(self.task.active)
    
    def test_mark_task_complete_no_done_stage(self):
        """Test marking task complete when no done stage exists."""
        # Temporarily remove done stages
        TaskStage.objects.filter(done=True).update(done=False)
        
        url = f'/api/tasks/{self.task.id}/mark_complete/'
        response = self.client.post(url)
        
        # Should return error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        
        # Restore done stage
        TaskStage.objects.filter(id=self.task.stage.id).update(done=True)
    
    def test_user_sees_own_tasks(self):
        """Test user sees tasks they own, co-own, or are responsible for."""
        url = '/api/tasks/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        task_ids = [t['id'] for t in results]
        # Should see own task
        self.assertIn(self.task.id, task_ids)
        # Should not see other user's task (unless responsible)
        if self.other_task.owner != self.user:
            self.assertNotIn(self.other_task.id, task_ids)
    
    def test_superuser_sees_all_tasks(self):
        """Test superuser sees all tasks."""
        self.client.force_authenticate(user=self.superuser)
        url = '/api/tasks/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        task_ids = [t['id'] for t in results]
        self.assertIn(self.task.id, task_ids)
        self.assertIn(self.other_task.id, task_ids)


@tag('APITest')
class ProjectAPITestCase(BaseTestCase, APITestCase):
    """Test Project API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_active=True
        )
        # Get default project stage
        project_stage = ProjectStage.objects.filter(default=True).first()
        if not project_stage:
            project_stage = ProjectStage.objects.first()
        
        from datetime import date, timedelta
        
        cls.project = Project.objects.create(
            name='Test Project',
            description='Test description',
            stage=project_stage,
            next_step='Test next step',
            next_step_date=date.today() + timedelta(days=7),
            owner=cls.user,
            active=True
        )
    
    def setUp(self):
        print(f"Run Test Method: {self._testMethodName}")
        self.client.force_authenticate(user=self.user)
    
    def test_list_projects(self):
        """Test listing projects."""
        url = '/api/projects/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_create_project(self):
        """Test creating a project."""
        from datetime import date, timedelta
        
        # Get default project stage
        project_stage = ProjectStage.objects.filter(default=True).first()
        if not project_stage:
            project_stage = ProjectStage.objects.first()
        
        url = '/api/projects/'
        data = {
            'name': 'New Project',
            'description': 'Project description',
            'stage': project_stage.id if project_stage else None,
            'next_step': 'Initial project setup',
            'next_step_date': (date.today() + timedelta(days=7)).isoformat(),
            'active': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Project')
    
    def test_get_project_detail(self):
        """Test retrieving project detail."""
        url = f'/api/projects/{self.project.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.project.id)
        self.assertEqual(response.data['name'], 'Test Project')

