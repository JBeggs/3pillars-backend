# API Tests

Comprehensive test suite for Django REST Framework API endpoints.

## Test Files

- `test_auth.py` - Authentication endpoints (login, refresh, list_users)
- `test_crm.py` - CRM endpoints (Company, Contact, Deal)
- `test_tasks.py` - Tasks endpoints (Task, Project)
- `test_permissions.py` - Permission and access control tests

## Running Tests

### Run All API Tests
```bash
python manage.py test tests.api --noinput
```

### Run Specific Test File
```bash
# Authentication tests
python manage.py test tests.api.test_auth --noinput

# CRM tests
python manage.py test tests.api.test_crm --noinput

# Tasks tests
python manage.py test tests.api.test_tasks --noinput

# Permissions tests
python manage.py test tests.api.test_permissions --noinput
```

### Run Specific Test Class
```bash
python manage.py test tests.api.test_auth.AuthAPITestCase --noinput
```

### Run Specific Test Method
```bash
python manage.py test tests.api.test_auth.AuthAPITestCase.test_login_success --noinput
```

### Keep Test Database (Faster)
```bash
python manage.py test tests.api --keepdb
```

## Test Coverage

### Authentication (`test_auth.py`)
- ✅ Successful login
- ✅ Login with missing credentials
- ✅ Login with invalid credentials
- ✅ Login with inactive user
- ✅ Token refresh
- ✅ Invalid refresh token
- ✅ List users (authenticated)
- ✅ List users excludes superuser
- ✅ List users excludes inactive users

### Company API (`test_crm.py`)
- ✅ List companies
- ✅ Filter companies by owner
- ✅ Superuser sees all companies
- ✅ Create company
- ✅ Auto-set owner on create
- ✅ Get company detail
- ✅ Update company
- ✅ Delete company
- ✅ Search companies
- ✅ Unauthorized access

### Contact API (`test_crm.py`)
- ✅ List contacts
- ✅ Create contact
- ✅ Get contact detail
- ✅ Update contact
- ✅ Delete contact

### Deal API (`test_crm.py`)
- ✅ List deals
- ✅ Create deal
- ✅ Get deal detail
- ✅ Update deal
- ✅ Change deal stage

### Task API (`test_tasks.py`)
- ✅ List tasks
- ✅ Filter tasks assigned to me
- ✅ Filter tasks created by me
- ✅ Create task
- ✅ Auto-set owner on create
- ✅ Create task with multiple responsible users
- ✅ Get task detail
- ✅ Update task
- ✅ Mark task complete
- ✅ User sees own tasks
- ✅ Superuser sees all tasks

### Project API (`test_tasks.py`)
- ✅ List projects
- ✅ Create project
- ✅ Get project detail

### Permissions (`test_permissions.py`)
- ✅ User can only see own companies
- ✅ Superuser sees all companies
- ✅ User cannot access other user's company
- ✅ User cannot update other user's company
- ✅ User cannot delete other user's company
- ✅ User can only see own contacts
- ✅ User can only see own deals
- ✅ Unauthorized access returns 401

## Test Structure

All tests inherit from:
- `BaseTestCase` - Provides fixtures and helper methods
- `APITestCase` - Provides API testing utilities

## Fixtures Used

Tests use fixtures from `BaseTestCase`:
- `currency.json`
- `test_country.json`
- `resolution.json`
- `groups.json`
- `department.json`
- `test_users.json`
- `deal_stage.json`
- `projectstage.json`
- `taskstage.json`
- `client_type.json`
- `closing_reason.json`
- `industry.json`
- `lead_source.json`
- `massmailsettings.json`

## Best Practices

1. **Isolation**: Each test is independent
2. **Cleanup**: Tests clean up after themselves
3. **Fixtures**: Use `setUpTestData` for class-level data
4. **Authentication**: Use `force_authenticate` for authenticated requests
5. **Assertions**: Use specific status codes and data checks
6. **Fail Hard**: Tests fail explicitly, no silent failures

## Adding New Tests

When adding new API endpoints:

1. Create test class inheriting from `BaseTestCase` and `APITestCase`
2. Use `@tag('APITest')` decorator
3. Set up test data in `setUpTestData` class method
4. Authenticate user in `setUp` method if needed
5. Test all CRUD operations
6. Test permissions and access control
7. Test error cases (validation, unauthorized, etc.)

Example:
```python
@tag('APITest')
class MyAPITestCase(BaseTestCase, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(...)
    
    def setUp(self):
        self.client.force_authenticate(user=self.user)
    
    def test_list_objects(self):
        url = '/api/myobjects/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

