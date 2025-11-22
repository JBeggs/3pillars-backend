"""
Tests for API permissions.
"""
from django.test import tag
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from crm.models import Company, Contact, Deal
from tests.base_test_classes import BaseTestCase

User = get_user_model()


@tag('APITest')
class PermissionsTestCase(BaseTestCase, APITestCase):
    """Test API permissions."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from django.contrib.auth.models import Group
        
        # Get or create separate groups for isolation
        group1, _ = Group.objects.get_or_create(name='Test Group 1')
        group2, _ = Group.objects.get_or_create(name='Test Group 2')
        
        cls.user1 = User.objects.create_user(
            username='user1',
            password='testpass123',
            email='user1@example.com',
            is_active=True
        )
        # Clear any groups from fixtures and add to isolated group
        cls.user1.groups.clear()
        cls.user1.groups.add(group1)
        
        cls.user2 = User.objects.create_user(
            username='user2',
            password='testpass123',
            email='user2@example.com',
            is_active=True
        )
        # Clear any groups from fixtures and add to different isolated group
        cls.user2.groups.clear()
        cls.user2.groups.add(group2)  # Different group for isolation
        
        cls.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        
        # Create test data
        cls.company1 = Company.objects.create(
            full_name='Company 1',
            owner=cls.user1
        )
        cls.company2 = Company.objects.create(
            full_name='Company 2',
            owner=cls.user2
        )
        
        cls.contact1 = Contact.objects.create(
            first_name='Contact',
            last_name='One',
            company=cls.company1,
            owner=cls.user1
        )
        
        from datetime import date, timedelta
        from crm.models import Stage
        from crm.utils.ticketproc import new_ticket
        
        stage = Stage.objects.first()
        # Generate unique ticket
        ticket = new_ticket()
        while Deal.objects.filter(ticket=ticket).exists():
            ticket = new_ticket()
        
        cls.deal1 = Deal.objects.create(
            name='Deal 1',
            company=cls.company1,
            next_step='Test next step',
            next_step_date=date.today() + timedelta(days=7),
            stage=stage,
            ticket=ticket,
            owner=cls.user1
        )
    
    def setUp(self):
        print(f"Run Test Method: {self._testMethodName}")
    
    def test_user_can_only_see_own_companies(self):
        """Test user can only see their own companies."""
        self.client.force_authenticate(user=self.user1)
        url = '/api/companies/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        company_ids = [c['id'] for c in results]
        # Should see own company
        self.assertIn(self.company1.id, company_ids)
        # Should not see other user's company
        self.assertNotIn(self.company2.id, company_ids)
    
    def test_superuser_sees_all_companies(self):
        """Test superuser sees all companies."""
        self.client.force_authenticate(user=self.superuser)
        url = '/api/companies/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        company_ids = [c['id'] for c in results]
        self.assertIn(self.company1.id, company_ids)
        self.assertIn(self.company2.id, company_ids)
    
    def test_user_cannot_access_other_users_company(self):
        """Test user cannot access other user's company detail."""
        self.client.force_authenticate(user=self.user1)
        url = f'/api/companies/{self.company2.id}/'
        response = self.client.get(url)
        
        # Should return 404 (not found) or 403 (forbidden)
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ])
    
    def test_user_cannot_update_other_users_company(self):
        """Test user cannot update other user's company."""
        self.client.force_authenticate(user=self.user1)
        url = f'/api/companies/{self.company2.id}/'
        data = {'full_name': 'Hacked Name'}
        response = self.client.patch(url, data, format='json')
        
        # Should return 404 or 403
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ])
        
        # Verify company was not updated
        self.company2.refresh_from_db()
        self.assertEqual(self.company2.full_name, 'Company 2')
    
    def test_user_cannot_delete_other_users_company(self):
        """Test user cannot delete other user's company."""
        self.client.force_authenticate(user=self.user1)
        url = f'/api/companies/{self.company2.id}/'
        response = self.client.delete(url)
        
        # Should return 404 or 403
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ])
        
        # Verify company still exists
        self.assertTrue(Company.objects.filter(id=self.company2.id).exists())
    
    def test_user_can_only_see_own_contacts(self):
        """Test user can only see their own contacts."""
        # Create contact for user2 (user2 is in different group)
        contact2 = Contact.objects.create(
            first_name='Contact',
            last_name='Two',
            company=self.company2,
            owner=self.user2
        )
        
        self.client.force_authenticate(user=self.user1)
        url = '/api/contacts/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        contact_ids = [c['id'] for c in results]
        # Should see own contact
        self.assertIn(self.contact1.id, contact_ids)
        # Should not see other user's contact (different groups)
        self.assertNotIn(contact2.id, contact_ids)
    
    def test_user_can_only_see_own_deals(self):
        """Test user can only see their own deals."""
        from datetime import date, timedelta
        from crm.models import Stage
        from crm.utils.ticketproc import new_ticket
        
        stage = Stage.objects.first()
        # Generate unique ticket
        ticket = new_ticket()
        while Deal.objects.filter(ticket=ticket).exists():
            ticket = new_ticket()
        
        deal2 = Deal.objects.create(
            name='Deal 2',
            company=self.company2,
            next_step='Test next step',
            next_step_date=date.today() + timedelta(days=7),
            stage=stage,
            ticket=ticket,
            owner=self.user2
        )
        
        self.client.force_authenticate(user=self.user1)
        url = '/api/deals/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        deal_ids = [d['id'] for d in results]
        # Should see own deal
        self.assertIn(self.deal1.id, deal_ids)
        # Should not see other user's deal
        self.assertNotIn(deal2.id, deal_ids)
    
    def test_unauthorized_access_returns_401(self):
        """Test unauthorized access returns 401."""
        self.client.force_authenticate(user=None)
        url = '/api/companies/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

