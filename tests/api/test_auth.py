"""
Tests for API authentication endpoints.
"""
from django.test import tag
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from tests.base_test_classes import BaseTestCase

User = get_user_model()


@tag('APITest')
class AuthAPITestCase(BaseTestCase, APITestCase):
    """Test authentication API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create test users
        cls.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        cls.inactive_user = User.objects.create_user(
            username='inactive',
            password='testpass123',
            email='inactive@example.com',
            is_active=False
        )
        cls.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
    
    def setUp(self):
        print(f"Run Test Method: {self._testMethodName}")
    
    def test_login_success(self):
        """Test successful login returns tokens and user data."""
        url = '/api/auth/login/'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_login_missing_username(self):
        """Test login with missing username returns error."""
        url = '/api/auth/login/'
        data = {'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Username is required')
    
    def test_login_missing_password(self):
        """Test login with missing password returns error."""
        url = '/api/auth/login/'
        data = {'username': 'testuser'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Password is required')
    
    def test_login_invalid_username(self):
        """Test login with invalid username returns error."""
        url = '/api/auth/login/'
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid username or password')
    
    def test_login_invalid_password(self):
        """Test login with invalid password returns error."""
        url = '/api/auth/login/'
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid username or password')
    
    def test_login_inactive_user(self):
        """Test login with inactive user returns error."""
        url = '/api/auth/login/'
        data = {
            'username': 'inactive',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertIn('inactive', response.data['error'].lower())
    
    def test_refresh_token(self):
        """Test token refresh endpoint."""
        # First login to get refresh token
        login_url = '/api/auth/login/'
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Refresh the token
        refresh_url = '/api/auth/refresh/'
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_refresh_token_invalid(self):
        """Test refresh token with invalid token returns error."""
        url = '/api/auth/refresh/'
        data = {'refresh': 'invalid_token'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_users_authenticated(self):
        """Test list users endpoint requires authentication."""
        url = '/api/auth/users/'
        
        # Without authentication
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With authentication
        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        # Check that superuser is excluded
        usernames = [user['username'] for user in response.data]
        self.assertNotIn('admin', usernames)
        self.assertIn('testuser', usernames)
    
    def test_list_users_excludes_superuser(self):
        """Test list users excludes superuser/admin."""
        self.client.force_authenticate(user=self.test_user)
        url = '/api/auth/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data]
        self.assertNotIn('admin', usernames)
    
    def test_list_users_excludes_inactive(self):
        """Test list users excludes inactive users."""
        self.client.force_authenticate(user=self.test_user)
        url = '/api/auth/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data]
        self.assertNotIn('inactive', usernames)

