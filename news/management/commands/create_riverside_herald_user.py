"""
Management command to create user for Riverside Herald Next.js app.
Creates user, company, and news profile with appropriate permissions.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from ecommerce.models import EcommerceCompany
from news.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Create user for Riverside Herald app with company and news profile"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='jody@riversideherald.co.za',
            help='User email address',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='defaultpassword123',
            help='User password',
        )
        parser.add_argument(
            '--company-name',
            type=str,
            default='Riverside Herald',
            help='Company name',
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=['admin', 'editor', 'author'],
            default='admin',
            help='News profile role (admin, editor, or author)',
        )
        parser.add_argument(
            '--full-name',
            type=str,
            default='Jody Beggs',
            help='User full name',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        company_name = options['company_name']
        role = options['role']
        full_name = options['full_name']

        self.stdout.write(self.style.SUCCESS('Creating Riverside Herald user...'))

        # Check if user already exists
        user = User.objects.filter(email=email).first()
        if user:
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists.'))
            self.stdout.write('Updating user...')
        else:
            # Create user
            username = email.split('@')[0]  # Use email prefix as username
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name.split()[0] if full_name else '',
                last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else '',
                is_active=True,
                is_staff=True,  # Allow admin panel access
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created user: {email}'))

        # Update user if needed
        if not user.is_active:
            user.is_active = True
        if not user.is_staff:
            user.is_staff = True
        user.save()

        # Check if company already exists
        company = EcommerceCompany.objects.filter(owner=user).first()
        if not company:
            # Create company
            company_slug = company_name.lower().replace(' ', '-').replace('_', '-')
            # Ensure slug is unique
            base_slug = company_slug
            counter = 1
            while EcommerceCompany.objects.filter(slug=company_slug).exists():
                company_slug = f"{base_slug}-{counter}"
                counter += 1

            company = EcommerceCompany.objects.create(
                name=company_name,
                slug=company_slug,
                email=email,
                owner=user,
                status='active',
                plan='premium',  # Give premium plan for full features
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created company: {company_name} (ID: {company.id})'))
        else:
            self.stdout.write(self.style.WARNING(f'Company already exists: {company.name} (ID: {company.id})'))

        # Create or update news profile
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'username': user.username,
                'full_name': full_name,
                'role': role,
                'is_verified': True,
            }
        )
        
        if not created:
            # Update existing profile
            profile.username = user.username
            profile.full_name = full_name
            profile.role = role
            profile.is_verified = True
            profile.save()
            self.stdout.write(self.style.WARNING('News profile already existed, updated it.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Created news profile with role: {role}'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Setup complete!'))
        self.stdout.write(self.style.SUCCESS('\n📋 User Details:'))
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  Full Name: {full_name}')
        self.stdout.write(f'  Role: {role}')
        self.stdout.write(f'  Is Staff: {user.is_staff}')
        self.stdout.write(f'  Is Active: {user.is_active}')
        
        self.stdout.write(self.style.SUCCESS('\n🏢 Company Details:'))
        self.stdout.write(f'  Name: {company.name}')
        self.stdout.write(f'  Slug: {company.slug}')
        self.stdout.write(f'  ID: {company.id}')
        self.stdout.write(f'  Status: {company.status}')
        self.stdout.write(f'  Plan: {company.plan}')
        
        self.stdout.write(self.style.SUCCESS('\n🔗 API Connection Info:'))
        self.stdout.write(f'  API Base URL: https://3pillars.pythonanywhere.com/api')
        self.stdout.write(f'  Login Endpoint: /api/auth/login/')
        self.stdout.write(f'  Company ID Header: X-Company-Id: {company.id}')
        self.stdout.write(f'  Auth Header: Authorization: Bearer <token>')
        
        self.stdout.write(self.style.SUCCESS('\n📝 Next Steps:'))
        self.stdout.write('  1. Update river-side-herald/.env.local with:')
        self.stdout.write(f'     NEXT_PUBLIC_API_URL=https://3pillars.pythonanywhere.com/api')
        self.stdout.write(f'     NEXT_PUBLIC_DEFAULT_COMPANY_ID={company.id}')
        self.stdout.write('  2. Test login with the credentials above')
        self.stdout.write('  3. Verify API endpoints are accessible')

