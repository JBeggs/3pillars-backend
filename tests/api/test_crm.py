"""
Tests for CRM API endpoints (Company, Contact, Deal, etc.).
"""
from decimal import Decimal
from datetime import date, timedelta
from django.test import tag
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from crm.models import Company, Contact, Deal, Stage
from crm.utils.ticketproc import new_ticket
from tests.base_test_classes import BaseTestCase

User = get_user_model()


@tag('APITest')
class CompanyAPITestCase(BaseTestCase, APITestCase):
    """Test Company API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from django.contrib.auth.models import Group
        
        # Get or create separate groups for isolation
        group1, _ = Group.objects.get_or_create(name='Test Group A')
        group2, _ = Group.objects.get_or_create(name='Test Group B')
        
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_active=True
        )
        # Clear any groups from fixtures and add to isolated group
        cls.user.groups.clear()
        cls.user.groups.add(group1)
        
        cls.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            email='other@example.com',
            is_active=True
        )
        # Clear any groups from fixtures and add to different isolated group
        cls.other_user.groups.clear()
        cls.other_user.groups.add(group2)  # Different group
        
        cls.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        
        # Create test companies with unique names
        cls.company1 = Company.objects.create(
            full_name='Test Company 1 Unique',
            email='company1@example.com',
            phone='+1-555-0101',
            owner=cls.user
        )
        cls.company2 = Company.objects.create(
            full_name='Test Company 2 Unique',
            email='company2@example.com',
            phone='+1-555-0102',
            owner=cls.other_user
        )
    
    def setUp(self):
        print(f"Run Test Method: {self._testMethodName}")
        self.client.force_authenticate(user=self.user)
    
    def test_list_companies(self):
        """Test listing companies."""
        url = '/api/companies/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_list_companies_filtered_by_owner(self):
        """Test companies are filtered by owner for non-superuser."""
        url = '/api/companies/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        # Should only see own companies
        for company in results:
            self.assertEqual(company['owner'], self.user.id)
    
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
    
    def test_create_company(self):
        """Test creating a company."""
        url = '/api/companies/'
        data = {
            'full_name': 'New Company Unique',
            'email': 'new@example.com',
            'phone': '+1-555-9999'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['full_name'], 'New Company Unique')
        self.assertEqual(response.data['owner'], self.user.id)
        
        # Verify it was created in database
        company = Company.objects.get(id=response.data['id'])
        self.assertEqual(company.owner, self.user)
    
    def test_create_company_auto_sets_owner(self):
        """Test that creating company automatically sets owner."""
        url = '/api/companies/'
        data = {
            'full_name': 'Auto Owner Company Unique',
            'email': 'auto@example.com'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.user.id)
    
    def test_get_company_detail(self):
        """Test retrieving company detail."""
        url = f'/api/companies/{self.company1.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.company1.id)
        self.assertEqual(response.data['full_name'], 'Test Company 1 Unique')
    
    def test_update_company(self):
        """Test updating a company."""
        url = f'/api/companies/{self.company1.id}/'
        data = {
            'full_name': 'Updated Company Name',
            'email': 'updated@example.com'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Updated Company Name')
        
        # Verify update in database
        self.company1.refresh_from_db()
        self.assertEqual(self.company1.full_name, 'Updated Company Name')
    
    def test_create_company_unique_together_constraint(self):
        """Test that unique_together constraint (full_name, country) is enforced."""
        url = '/api/companies/'
        # Create first company
        data1 = {
            'full_name': 'Duplicate Name',
            'email': 'first@example.com'
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to create duplicate (same name, same country=None)
        data2 = {
            'full_name': 'Duplicate Name',
            'email': 'second@example.com'
        }
        response2 = self.client.post(url, data2, format='json')
        # Should fail due to unique_together constraint
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_company(self):
        """Test deleting a company."""
        company = Company.objects.create(
            full_name='To Delete',
            owner=self.user
        )
        url = f'/api/companies/{company.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.objects.filter(id=company.id).exists())
    
    def test_search_companies(self):
        """Test searching companies."""
        url = '/api/companies/?search=Company 1'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertGreater(len(results), 0)
        # Should find company1
        company_ids = [c['id'] for c in results]
        self.assertIn(self.company1.id, company_ids)
    
    def test_unauthorized_access(self):
        """Test unauthorized access returns 401."""
        self.client.force_authenticate(user=None)
        url = '/api/companies/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@tag('APITest')
class ContactAPITestCase(BaseTestCase, APITestCase):
    """Test Contact API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_active=True
        )
        cls.company = Company.objects.create(
            full_name='Test Company',
            owner=cls.user
        )
        cls.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1-555-0101',
            company=cls.company,
            owner=cls.user
        )
    
    def setUp(self):
        print(f"Run Test Method: {self._testMethodName}")
        self.client.force_authenticate(user=self.user)
    
    def test_list_contacts(self):
        """Test listing contacts."""
        url = '/api/contacts/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_create_contact(self):
        """Test creating a contact."""
        url = '/api/contacts/'
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone': '+1-555-0202',
            'company': self.company.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['company'], self.company.id)
    
    def test_get_contact_detail(self):
        """Test retrieving contact detail."""
        url = f'/api/contacts/{self.contact.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.contact.id)
        self.assertEqual(response.data['first_name'], 'John')
    
    def test_update_contact(self):
        """Test updating a contact."""
        url = f'/api/contacts/{self.contact.id}/'
        data = {'first_name': 'Johnny'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Johnny')
    
    def test_delete_contact(self):
        """Test deleting a contact."""
        contact = Contact.objects.create(
            first_name='To Delete',
            company=self.company,
            owner=self.user
        )
        url = f'/api/contacts/{contact.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Contact.objects.filter(id=contact.id).exists())


@tag('APITest')
class DealAPITestCase(BaseTestCase, APITestCase):
    """Test Deal API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_active=True
        )
        cls.company = Company.objects.create(
            full_name='Test Company',
            owner=cls.user
        )
        cls.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            company=cls.company,
            owner=cls.user
        )
        cls.stage = Stage.objects.first()
        # Generate unique ticket
        ticket = new_ticket()
        while Deal.objects.filter(ticket=ticket).exists():
            ticket = new_ticket()
        
        cls.deal = Deal.objects.create(
            name='Test Deal',
            company=cls.company,
            contact=cls.contact,
            amount=Decimal('50000.00'),
            stage=cls.stage,
            next_step='Test next step',
            next_step_date=date.today() + timedelta(days=7),
            ticket=ticket,
            owner=cls.user
        )
    
    def setUp(self):
        print(f"Run Test Method: {self._testMethodName}")
        self.client.force_authenticate(user=self.user)
    
    def test_list_deals(self):
        """Test listing deals."""
        url = '/api/deals/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_create_deal(self):
        """Test creating a deal."""
        url = '/api/deals/'
        data = {
            'name': 'New Deal',
            'company': self.company.id,
            'contact': self.contact.id,
            'amount': '75000.00',
            'stage': self.stage.id if self.stage else None,
            'next_step': 'Send proposal',
            'next_step_date': (date.today() + timedelta(days=14)).isoformat(),
            'description': 'Test deal description',
            'workflow': 'Test workflow notes'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Deal')
        self.assertEqual(response.data['company'], self.company.id)
        # Verify ticket was auto-generated
        self.assertIsNotNone(response.data.get('ticket'))
    
    def test_get_deal_detail(self):
        """Test retrieving deal detail."""
        url = f'/api/deals/{self.deal.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.deal.id)
        self.assertEqual(response.data['name'], 'Test Deal')
    
    def test_update_deal(self):
        """Test updating a deal."""
        url = f'/api/deals/{self.deal.id}/'
        data = {'name': 'Updated Deal Name'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Deal Name')
    
    def test_change_deal_stage(self):
        """Test changing deal stage."""
        new_stage = Stage.objects.exclude(id=self.stage.id).first()
        if new_stage:
            url = f'/api/deals/{self.deal.id}/change_stage/'
            data = {'stage_id': new_stage.id}
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.deal.refresh_from_db()
            self.assertEqual(self.deal.stage.id, new_stage.id)
    
    def test_create_deal_with_required_fields(self):
        """Test creating a deal with all required fields."""
        url = '/api/deals/'
        data = {
            'name': 'Required Fields Deal',
            'company': self.company.id,
            'contact': self.contact.id,
            'amount': '60000.00',
            'stage': self.stage.id if self.stage else None,
            'next_step': 'Required next step',
            'next_step_date': (date.today() + timedelta(days=14)).isoformat(),
            'description': 'Test description'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Required Fields Deal')
        # Verify ticket was auto-generated
        self.assertIsNotNone(response.data.get('ticket'))

