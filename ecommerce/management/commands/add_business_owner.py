"""
Management command to add a business owner to the CRM.
Creates user, company, integration settings, and Riverside Herald access.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify
from ecommerce.models import EcommerceCompany, CompanyIntegrationSettings
from news.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Add a business owner with company, integration settings, and Riverside Herald access"

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='JavaMellow',
            help='Business/Company name (default: JavaMellow)',
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Business owner email address (required)',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username (default: email prefix)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='changeme123',
            help='User password (default: changeme123)',
        )
        parser.add_argument(
            '--full-name',
            type=str,
            default='Business Owner',
            help='Full name (default: Business Owner)',
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='+27 12 345 6789',
            help='Phone number',
        )
        parser.add_argument(
            '--city',
            type=str,
            default='Pretoria',
            help='City (default: Pretoria)',
        )
        parser.add_argument(
            '--province',
            type=str,
            default='Gauteng',
            help='Province (default: Gauteng)',
        )
        parser.add_argument(
            '--postal-code',
            type=str,
            default='0001',
            help='Postal code (default: 0001)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        company_name = options['name']
        email = options['email']
        username = options.get('username')
        password = options['password']
        full_name = options['full_name']
        phone = options['phone']
        city = options['city']
        province = options['province']
        postal_code = options['postal_code']

        self.stdout.write(self.style.SUCCESS('Creating business owner...'))

        # Step 1: Create or get User
        user = User.objects.filter(email=email).first()
        if user:
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists. Updating...'))
            if not user.is_active:
                user.is_active = True
            if not user.is_staff:
                user.is_staff = True
            user.save()
        else:
            # Generate username from email if not provided
            if not username:
                username = email.split('@')[0]
            
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Split full name
            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_staff=True,  # Allow admin panel access
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created user: {email} ({username})'))

        # Step 2: Create or get EcommerceCompany
        company = EcommerceCompany.objects.filter(owner=user).first()
        if company:
            self.stdout.write(self.style.WARNING(f'Company already exists for user: {company.name}'))
        else:
            # Generate slug from company name
            company_slug = slugify(company_name)
            base_slug = company_slug
            counter = 1
            while EcommerceCompany.objects.filter(slug=company_slug).exists():
                company_slug = f"{base_slug}-{counter}"
                counter += 1

            company = EcommerceCompany.objects.create(
                name=company_name,
                slug=company_slug,
                email=email,
                phone=phone,
                owner=user,
                address_street='123 Main Street',
                address_city=city,
                address_province=province,
                address_postal_code=postal_code,
                address_country='ZA',
                registration_number='REG123456',
                tax_number='VAT123456',
                status='active',
                plan='premium',
                currency='ZAR',
                timezone='Africa/Johannesburg',
                language='en',
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created company: {company_name} (ID: {company.id})'))

        # Step 3: Create CompanyIntegrationSettings with placeholder API keys
        integration_settings, created = CompanyIntegrationSettings.objects.get_or_create(
            company=company,
            defaults={
                'payment_gateway': 'yoco',
                'yoco_secret_key': 'sk_test_placeholder_replace_with_real_key',
                'yoco_public_key': 'pk_test_placeholder_replace_with_real_key',
                'yoco_webhook_secret': 'whsec_placeholder_replace_with_real_secret',
                'yoco_sandbox_mode': True,
                'courier_service': 'courier_guy',
                'courier_guy_api_key': 'api_key_placeholder_replace_with_real_key',
                'courier_guy_api_secret': 'api_secret_placeholder_replace_with_real_secret',
                'courier_guy_account_number': 'ACC123456',
                'courier_guy_sandbox_mode': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created integration settings with placeholder API keys'))
        else:
            self.stdout.write(self.style.WARNING('Integration settings already exist'))

        # Step 4: Find or create Riverside Herald company
        riverside_company = None
        for name_variant in ['Riverside Herald', 'riverside-herald', 'riversideherald']:
            riverside_company = EcommerceCompany.objects.filter(
                name__iexact=name_variant
            ).first() or EcommerceCompany.objects.filter(
                slug__iexact=slugify(name_variant)
            ).first()
            if riverside_company:
                break

        if not riverside_company:
            # Create Riverside Herald company if it doesn't exist
            self.stdout.write(self.style.WARNING('Riverside Herald company not found. Creating it...'))
            riverside_company = EcommerceCompany.objects.create(
                name='Riverside Herald',
                slug='riverside-herald',
                email='admin@riversideherald.co.za',
                owner=user,  # Use the business owner as initial owner
                status='active',
                plan='premium',
                currency='ZAR',
                timezone='Africa/Johannesburg',
                language='en',
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created Riverside Herald company (ID: {riverside_company.id})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Found Riverside Herald company: {riverside_company.name}'))

        # Step 5: Add user as member of Riverside Herald company (for content management)
        if hasattr(riverside_company, 'users'):
            if not riverside_company.users.filter(id=user.id).exists():
                riverside_company.users.add(user)
                self.stdout.write(self.style.SUCCESS('✓ Added user as member of Riverside Herald company'))
            else:
                self.stdout.write(self.style.WARNING('User already a member of Riverside Herald'))

        # Step 6: Create or update news Profile for Riverside Herald access
        profile, profile_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'username': user.username,
                'full_name': full_name,
                'role': 'business_owner',  # Business owners can manage content
                'is_verified': True,
            }
        )
        
        if not profile_created:
            # Update existing profile
            profile.username = user.username
            profile.full_name = full_name
            profile.role = 'business_owner'
            profile.is_verified = True
            profile.save()
            self.stdout.write(self.style.WARNING('News profile already existed, updated it.'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Created news profile with role: business_owner'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Setup complete!'))
        self.stdout.write(self.style.SUCCESS('\n📋 User Details:'))
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  Full Name: {full_name}')
        self.stdout.write(f'  Is Staff: {user.is_staff}')
        self.stdout.write(f'  Is Active: {user.is_active}')
        
        self.stdout.write(self.style.SUCCESS('\n🏢 Business Company Details:'))
        self.stdout.write(f'  Name: {company.name}')
        self.stdout.write(f'  Slug: {company.slug}')
        self.stdout.write(f'  ID: {company.id}')
        self.stdout.write(f'  Status: {company.status}')
        self.stdout.write(f'  Plan: {company.plan}')
        
        self.stdout.write(self.style.SUCCESS('\n🔑 Integration Settings:'))
        self.stdout.write(f'  Yoco Public Key: {integration_settings.yoco_public_key}')
        self.stdout.write(f'  Yoco Sandbox Mode: {integration_settings.yoco_sandbox_mode}')
        self.stdout.write(f'  Courier Service: {integration_settings.courier_service}')
        self.stdout.write(f'  Courier Sandbox Mode: {integration_settings.courier_guy_sandbox_mode}')
        self.stdout.write(self.style.WARNING('  ⚠️  Remember to replace placeholder API keys with real keys!'))
        
        self.stdout.write(self.style.SUCCESS('\n📰 Riverside Herald Access:'))
        self.stdout.write(f'  Company: {riverside_company.name}')
        self.stdout.write(f'  Company ID: {riverside_company.id}')
        self.stdout.write(f'  News Profile Role: {profile.role}')
        self.stdout.write(f'  Can Manage Content: Yes')
        
        self.stdout.write(self.style.SUCCESS('\n🔗 API Connection Info:'))
        self.stdout.write(f'  API Base URL: http://localhost:8000/api/v1 (or your production URL)')
        self.stdout.write(f'  Login Endpoint: /api/auth/login/')
        self.stdout.write(f'  Business Company ID Header: X-Company-Id: {company.id}')
        self.stdout.write(f'  Riverside Herald ID Header: X-Company-Id: {riverside_company.id}')
        self.stdout.write(f'  Auth Header: Authorization: Bearer <token>')
        
        self.stdout.write(self.style.SUCCESS('\n📝 Next Steps:'))
        self.stdout.write('  1. Update integration settings with real Yoco API keys')
        self.stdout.write('  2. Update integration settings with real Courier Guy API keys')
        self.stdout.write('  3. Test login with the credentials above')
        self.stdout.write('  4. Verify access to Riverside Herald content management')
        self.stdout.write('  5. Add products to the business company')

