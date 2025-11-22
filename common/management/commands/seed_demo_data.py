"""
Seed demo data for CRM showcase.
Creates users, companies, contacts, deals, tasks, and projects.
"""
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db import transaction

from crm.models import Company, Contact, Deal, Lead, Stage, Country, Currency, ClientType, Industry, LeadSource
from crm.utils.ticketproc import new_ticket
from tasks.models import Task, Project, TaskStage, ProjectStage
from tasks.models.taskbase import TaskBase

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data for CRM showcase"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing demo data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting demo data seeding...'))

        # Get or create required lookup data
        self._setup_lookup_data()

        # Create users
        admin_user = self._create_admin_user()
        jody_user = self._create_user('jody', 'jody123', 'Jody', 'Beggs', 'jody@example.com', is_staff=True)
        debbie_user = self._create_user('debbie', 'debbie123', 'Debbie', 'Smith', 'debbie@example.com', is_staff=True)
        barden_user = self._create_user('barden', 'barden123', 'Barden', 'Johnson', 'barden@example.com', is_staff=True)

        # Get departments/groups
        sales_group = Group.objects.filter(name__icontains='sales').first()
        tech_group = Group.objects.filter(name__icontains='technical').first() or Group.objects.first()

        # Assign users to groups
        if sales_group:
            barden_user.groups.add(sales_group)
        if tech_group:
            jody_user.groups.add(tech_group)
            debbie_user.groups.add(tech_group)

        # Create companies
        companies = self._create_companies([jody_user, debbie_user, barden_user], sales_group)

        # Create contacts
        contacts = self._create_contacts(companies, [jody_user, debbie_user, barden_user])

        # Create deals
        deals = self._create_deals(companies, contacts, [jody_user, debbie_user, barden_user], sales_group)

        # Create projects
        projects = self._create_projects([jody_user, debbie_user, barden_user])

        # Create tasks
        self._create_tasks(projects, deals, [jody_user, debbie_user, barden_user])

        # Create some leads
        self._create_leads([jody_user, barden_user], sales_group)

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('\n📋 Login Credentials:'))
        self.stdout.write(self.style.SUCCESS('  Admin: admin / Defcon12'))
        self.stdout.write(self.style.SUCCESS('  Jody: jody / jody123'))
        self.stdout.write(self.style.SUCCESS('  Debbie: debbie / debbie123'))
        self.stdout.write(self.style.SUCCESS('  Barden: barden / barden123'))

    def _setup_lookup_data(self):
        """Get or create required lookup data."""
        # Get default country (USA)
        self.country_usa = Country.objects.filter(name__icontains='united states').first() or \
                           Country.objects.filter(name__icontains='usa').first() or \
                           Country.objects.first()

        # Get default currency (USD)
        self.currency_usd = Currency.objects.filter(name='USD').first() or Currency.objects.first()

        # Get client types
        self.client_type_reseller = ClientType.objects.filter(name__icontains='reseller').first() or \
                                   ClientType.objects.first()
        self.client_type_end_customer = ClientType.objects.filter(name__icontains='end').first() or \
                                       ClientType.objects.first()

        # Get industries
        self.industry_tech = Industry.objects.filter(name__icontains='technology').first() or \
                            Industry.objects.filter(name__icontains='it').first() or \
                            Industry.objects.first()

        # Get lead sources
        self.lead_source_website = LeadSource.objects.filter(name__icontains='website').first() or \
                                   LeadSource.objects.first()

        # Get deal stages
        self.stage_request = Stage.objects.filter(name='request').first() or \
                            Stage.objects.filter(default=True).first() or \
                            Stage.objects.first()
        self.stage_analysis = Stage.objects.filter(name__icontains='analysis').first() or \
                             Stage.objects.filter(second_default=True).first() or \
                             Stage.objects.all()[1] if Stage.objects.count() > 1 else self.stage_request
        self.stage_proposal = Stage.objects.filter(name__icontains='proposal').first() or \
                             Stage.objects.filter(name__icontains='offer').first() or \
                             Stage.objects.all()[3] if Stage.objects.count() > 3 else self.stage_analysis
        self.stage_agreement = Stage.objects.filter(name__icontains='agreement').first() or \
                              Stage.objects.filter(success_stage=True).first() or \
                              Stage.objects.last()

        # Get task stages
        self.task_stage_pending = TaskStage.objects.filter(name='pending').first() or \
                                 TaskStage.objects.filter(default=True).first() or \
                                 TaskStage.objects.first()
        self.task_stage_in_progress = TaskStage.objects.filter(name__icontains='progress').first() or \
                                     TaskStage.objects.filter(in_progress=True).first() or \
                                     TaskStage.objects.all()[1] if TaskStage.objects.count() > 1 else self.task_stage_pending
        self.task_stage_completed = TaskStage.objects.filter(name='completed').first() or \
                                   TaskStage.objects.filter(done=True).first() or \
                                   TaskStage.objects.last()

        # Get project stages
        self.project_stage_pending = ProjectStage.objects.filter(name='pending').first() or \
                                    ProjectStage.objects.filter(default=True).first() or \
                                    ProjectStage.objects.first()
        self.project_stage_in_progress = ProjectStage.objects.filter(name__icontains='progress').first() or \
                                        ProjectStage.objects.filter(in_progress=True).first() or \
                                        ProjectStage.objects.all()[1] if ProjectStage.objects.count() > 1 else self.project_stage_pending

    def _create_admin_user(self):
        """Create admin superuser."""
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
            }
        )
        if created:
            user.set_password('Defcon12')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created admin user'))
        else:
            user.set_password('Defcon12')
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.WARNING(f'  ⚠ Updated existing admin user'))
        return user

    def _create_user(self, username, password, first_name, last_name, email, is_staff=False):
        """Create regular user."""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': is_staff,
                'is_active': True,
            }
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created user: {username}'))
        else:
            user.set_password(password)
            user.is_staff = is_staff
            user.save()
            self.stdout.write(self.style.WARNING(f'  ⚠ Updated existing user: {username}'))
        return user

    def _create_companies(self, owners, department):
        """Create demo companies."""
        companies_data = [
            {
                'full_name': 'TechFlow Solutions Inc.',
                'alternative_names': 'TechFlow, TFS',
                'website': 'https://techflow.com',
                'phone': '+1-555-0101',
                'email': 'info@techflow.com',
                'city_name': 'San Francisco',
                'registration_number': 'TF-2024-001',
                'owner': owners[0],  # Jody
            },
            {
                'full_name': 'Global Manufacturing Corp',
                'alternative_names': 'GMC, Global Mfg',
                'website': 'https://globalmfg.com',
                'phone': '+1-555-0202',
                'email': 'contact@globalmfg.com',
                'city_name': 'Chicago',
                'registration_number': 'GM-2024-002',
                'owner': owners[1],  # Debbie
            },
            {
                'full_name': 'CloudScale Technologies',
                'alternative_names': 'CloudScale, CST',
                'website': 'https://cloudscale.io',
                'phone': '+1-555-0303',
                'email': 'hello@cloudscale.io',
                'city_name': 'Austin',
                'registration_number': 'CS-2024-003',
                'owner': owners[2],  # Barden
            },
            {
                'full_name': 'DataVault Systems',
                'alternative_names': 'DataVault, DVS',
                'website': 'https://datavault.com',
                'phone': '+1-555-0404',
                'email': 'sales@datavault.com',
                'city_name': 'Seattle',
                'registration_number': 'DV-2024-004',
                'owner': owners[0],  # Jody
            },
            {
                'full_name': 'InnovateNow Industries',
                'alternative_names': 'InnovateNow, INI',
                'website': 'https://innovatnow.com',
                'phone': '+1-555-0505',
                'email': 'info@innovatnow.com',
                'city_name': 'Boston',
                'registration_number': 'IN-2024-005',
                'owner': owners[1],  # Debbie
            },
        ]

        companies = []
        for data in companies_data:
            company, created = Company.objects.get_or_create(
                full_name=data['full_name'],
                country=self.country_usa,
                defaults={
                    **{k: v for k, v in data.items() if k != 'full_name'},
                    'country': self.country_usa,
                    'type': self.client_type_end_customer,
                    'department': department,
                }
            )
            if created:
                company.industry.add(self.industry_tech)
            companies.append(company)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(companies)} companies'))
        return companies

    def _create_contacts(self, companies, owners):
        """Create demo contacts."""
        contacts_data = [
            {'first_name': 'Sarah', 'last_name': 'Chen', 'email': 'sarah.chen@techflow.com',
             'phone': '+1-555-1101', 'company': companies[0], 'owner': owners[0]},
            {'first_name': 'Michael', 'last_name': 'Rodriguez', 'email': 'm.rodriguez@globalmfg.com',
             'phone': '+1-555-1202', 'company': companies[1], 'owner': owners[1]},
            {'first_name': 'Emily', 'last_name': 'Watson', 'email': 'emily@cloudscale.io',
             'phone': '+1-555-1303', 'company': companies[2], 'owner': owners[2]},
            {'first_name': 'David', 'last_name': 'Kim', 'email': 'david.kim@datavault.com',
             'phone': '+1-555-1404', 'company': companies[3], 'owner': owners[0]},
            {'first_name': 'Lisa', 'last_name': 'Anderson', 'email': 'lisa@innovatnow.com',
             'phone': '+1-555-1505', 'company': companies[4], 'owner': owners[1]},
            {'first_name': 'James', 'last_name': 'Taylor', 'email': 'james.taylor@techflow.com',
             'phone': '+1-555-1102', 'company': companies[0], 'owner': owners[2]},
            {'first_name': 'Rachel', 'last_name': 'Martinez', 'email': 'rachel.martinez@techflow.com',
             'phone': '+1-555-1103', 'company': companies[0], 'owner': owners[0]},
            {'first_name': 'Thomas', 'last_name': 'Brown', 'email': 'thomas.brown@globalmfg.com',
             'phone': '+1-555-1203', 'company': companies[1], 'owner': owners[1]},
            {'first_name': 'Jessica', 'last_name': 'Lee', 'email': 'jessica.lee@cloudscale.io',
             'phone': '+1-555-1304', 'company': companies[2], 'owner': owners[2]},
            {'first_name': 'Robert', 'last_name': 'Wilson', 'email': 'robert.wilson@datavault.com',
             'phone': '+1-555-1405', 'company': companies[3], 'owner': owners[0]},
            {'first_name': 'Amanda', 'last_name': 'Garcia', 'email': 'amanda.garcia@innovatnow.com',
             'phone': '+1-555-1506', 'company': companies[4], 'owner': owners[1]},
            {'first_name': 'Christopher', 'last_name': 'Moore', 'email': 'christopher.moore@techflow.com',
             'phone': '+1-555-1104', 'company': companies[0], 'owner': owners[2]},
            {'first_name': 'Jennifer', 'last_name': 'Jackson', 'email': 'jennifer.jackson@globalmfg.com',
             'phone': '+1-555-1204', 'company': companies[1], 'owner': owners[0]},
            {'first_name': 'Daniel', 'last_name': 'White', 'email': 'daniel.white@cloudscale.io',
             'phone': '+1-555-1305', 'company': companies[2], 'owner': owners[1]},
        ]

        contacts = []
        for data in contacts_data:
            contact, created = Contact.objects.get_or_create(
                email=data['email'],
                defaults={
                    **{k: v for k, v in data.items() if k != 'email'},
                    'country': self.country_usa,
                }
            )
            contacts.append(contact)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(contacts)} contacts'))
        return contacts

    def _create_deals(self, companies, contacts, owners, department):
        """Create demo deals."""
        today = timezone.now().date()
        deals_data = [
            {
                'name': 'TechFlow Enterprise License',
                'description': 'Multi-year enterprise license for TechFlow Solutions',
                'amount': Decimal('125000.00'),
                'stage': self.stage_proposal,
                'next_step': 'Send final proposal and schedule contract review',
                'next_step_date': today + timedelta(days=5),
                'probability': 75,
                'company': companies[0],
                'contact': contacts[0],
                'owner': owners[0],  # Jody
                'co_owner': owners[2],  # Barden
            },
            {
                'name': 'Global Manufacturing Automation System',
                'description': 'Full automation system implementation',
                'amount': Decimal('450000.00'),
                'stage': self.stage_analysis,
                'next_step': 'Complete requirements analysis and prepare technical proposal',
                'next_step_date': today + timedelta(days=10),
                'probability': 60,
                'company': companies[1],
                'contact': contacts[1],
                'owner': owners[1],  # Debbie
            },
            {
                'name': 'CloudScale Infrastructure Migration',
                'description': 'Migrate legacy systems to cloud infrastructure',
                'amount': Decimal('280000.00'),
                'stage': self.stage_agreement,
                'next_step': 'Finalize contract terms and schedule kickoff meeting',
                'next_step_date': today + timedelta(days=3),
                'probability': 90,
                'company': companies[2],
                'contact': contacts[2],
                'owner': owners[2],  # Barden
                'important': True,
            },
            {
                'name': 'DataVault Security Upgrade',
                'description': 'Security infrastructure upgrade and compliance audit',
                'amount': Decimal('95000.00'),
                'stage': self.stage_request,
                'next_step': 'Initial consultation and security assessment',
                'next_step_date': today + timedelta(days=7),
                'probability': 40,
                'company': companies[3],
                'contact': contacts[3],
                'owner': owners[0],  # Jody
            },
            {
                'name': 'InnovateNow R&D Platform',
                'description': 'Research and development platform implementation',
                'amount': Decimal('320000.00'),
                'stage': self.stage_proposal,
                'next_step': 'Present proposal to board and address questions',
                'next_step_date': today + timedelta(days=14),
                'probability': 70,
                'company': companies[4],
                'contact': contacts[4],
                'owner': owners[1],  # Debbie
                'co_owner': owners[0],  # Jody
            },
            {
                'name': 'IT developments',
                'description': 'From email campaign to micro websites 3 to 5 pages and one full app development like this one django crm backend and flutter front end',
                'amount': Decimal('150000.00'),
                'stage': self.stage_analysis,
                'next_step': 'Requirements gathering and technical planning',
                'next_step_date': today + timedelta(days=7),
                'probability': 65,
                'company': companies[0],
                'contact': contacts[0],
                'owner': owners[0],  # Jody
                'co_owner': owners[1],  # Debbie
            },
        ]

        deals = []
        for data in deals_data:
            # Generate unique ticket for each deal
            ticket = new_ticket()
            # Ensure ticket is unique (retry if collision, though extremely unlikely)
            while Deal.objects.filter(ticket=ticket).exists():
                ticket = new_ticket()
            
            deal = Deal.objects.create(
                **{k: v for k, v in data.items()},
                ticket=ticket,
                currency=self.currency_usd,
                department=department,
            )
            deals.append(deal)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(deals)} deals'))
        return deals

    def _create_projects(self, owners):
        """Create demo projects."""
        today = timezone.now().date()
        projects_data = [
            {
                'name': 'Q1 Product Launch',
                'description': 'Launch new product line in Q1',
                'stage': self.project_stage_in_progress,
                'owner': owners[1],  # Debbie
                'co_owner': owners[0],  # Jody
                'due_date': today + timedelta(days=45),
                'start_date': today - timedelta(days=30),
                'priority': TaskBase.HIGH,
                'next_step': 'Complete final testing and prepare launch materials',
                'next_step_date': today + timedelta(days=5),
            },
            {
                'name': 'Customer Onboarding Automation',
                'description': 'Automate customer onboarding process',
                'stage': self.project_stage_pending,
                'owner': owners[0],  # Jody
                'due_date': today + timedelta(days=60),
                'start_date': today + timedelta(days=7),
                'priority': TaskBase.MIDDLE,
                'next_step': 'Kickoff meeting and requirements gathering',
                'next_step_date': today + timedelta(days=7),
            },
            {
                'name': 'Sales Training Program',
                'description': 'Develop and implement sales training program',
                'stage': self.project_stage_in_progress,
                'owner': owners[2],  # Barden
                'due_date': today + timedelta(days=30),
                'start_date': today - timedelta(days=15),
                'priority': TaskBase.HIGH,
                'next_step': 'Complete module 3 and schedule practice sessions',
                'next_step_date': today + timedelta(days=3),
            },
        ]

        projects = []
        for data in projects_data:
            project = Project.objects.create(**data)
            project.responsible.add(data['owner'])
            if 'co_owner' in data and data['co_owner']:
                project.responsible.add(data['co_owner'])
            projects.append(project)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(projects)} projects'))
        return projects

    def _create_tasks(self, projects, deals, owners):
        """Create demo tasks."""
        today = timezone.now().date()
        tasks_data = [
            # Tasks for Q1 Product Launch project
            {
                'name': 'Finalize product specifications',
                'description': 'Review and approve final product specifications',
                'project': projects[0],
                'stage': self.task_stage_completed,
                'owner': owners[0],  # Jody
                'due_date': today - timedelta(days=5),
                'priority': TaskBase.HIGH,
                'next_step': 'Done',
                'next_step_date': today,
            },
            {
                'name': 'Prepare marketing materials',
                'description': 'Create brochures, website content, and press releases',
                'project': projects[0],
                'stage': self.task_stage_in_progress,
                'owner': owners[1],  # Debbie
                'due_date': today + timedelta(days=10),
                'priority': TaskBase.HIGH,
                'next_step': 'Review draft with marketing team',
                'next_step_date': today + timedelta(days=2),
            },
            {
                'name': 'Conduct beta testing',
                'description': 'Run beta tests with selected customers',
                'project': projects[0],
                'stage': self.task_stage_in_progress,
                'owner': owners[0],  # Jody
                'due_date': today + timedelta(days=20),
                'priority': TaskBase.MIDDLE,
                'next_step': 'Schedule beta test sessions',
                'next_step_date': today + timedelta(days=3),
            },
            # Tasks for Customer Onboarding Automation project
            {
                'name': 'Design onboarding workflow',
                'description': 'Map out the complete onboarding workflow',
                'project': projects[1],
                'stage': self.task_stage_pending,
                'owner': owners[0],  # Jody
                'due_date': today + timedelta(days=14),
                'priority': TaskBase.MIDDLE,
                'next_step': 'Start workflow design session',
                'next_step_date': today + timedelta(days=7),
            },
            # Tasks for Sales Training Program project
            {
                'name': 'Create training modules',
                'description': 'Develop training content for modules 1-3',
                'project': projects[2],
                'stage': self.task_stage_in_progress,
                'owner': owners[2],  # Barden
                'due_date': today + timedelta(days=15),
                'priority': TaskBase.HIGH,
                'next_step': 'Complete module 3 content',
                'next_step_date': today + timedelta(days=2),
            },
            {
                'name': 'Schedule training sessions',
                'description': 'Book rooms and notify participants',
                'project': projects[2],
                'stage': self.task_stage_pending,
                'owner': owners[1],  # Debbie
                'due_date': today + timedelta(days=7),
                'priority': TaskBase.MIDDLE,
                'next_step': 'Send calendar invites',
                'next_step_date': today + timedelta(days=1),
            },
            # Standalone tasks (not in projects)
            {
                'name': 'Follow up on TechFlow proposal',
                'description': 'Call Sarah Chen to discuss proposal details',
                'stage': self.task_stage_pending,
                'owner': owners[0],  # Jody
                'due_date': today + timedelta(days=2),
                'priority': TaskBase.HIGH,
                'next_step': 'Schedule call',
                'next_step_date': today + timedelta(days=1),
            },
            {
                'name': 'Review CloudScale contract',
                'description': 'Legal review of CloudScale contract terms',
                'stage': self.task_stage_pending,
                'owner': owners[2],  # Barden
                'due_date': today + timedelta(days=5),
                'priority': TaskBase.HIGH,
                'next_step': 'Send to legal team',
                'next_step_date': today + timedelta(days=1),
            },
            {
                'name': 'Prepare quarterly report',
                'description': 'Compile Q1 sales and performance metrics',
                'stage': self.task_stage_pending,
                'owner': owners[1],  # Debbie
                'due_date': today + timedelta(days=14),
                'priority': TaskBase.MIDDLE,
                'next_step': 'Gather data from all departments',
                'next_step_date': today + timedelta(days=3),
            },
        ]

        tasks = []
        for data in tasks_data:
            task = Task.objects.create(**{k: v for k, v in data.items() if k != 'owner'})
            task.responsible.add(data['owner'])
            tasks.append(task)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(tasks)} tasks'))
        return tasks

    def _create_leads(self, owners, department):
        """Create demo leads."""
        # owners[0] = jody_user, owners[1] = barden_user
        leads_data = [
            {
                'first_name': 'Robert',
                'last_name': 'Martinez',
                'email': 'robert.martinez@newtech.com',
                'phone': '+1-555-2001',
                'company_name': 'NewTech Innovations',
                'website': 'https://newtech.com',
                'owner': owners[1],  # Barden (index 1)
            },
            {
                'first_name': 'Jennifer',
                'last_name': 'White',
                'email': 'jennifer@startupco.io',
                'phone': '+1-555-2002',
                'company_name': 'StartupCo',
                'website': 'https://startupco.io',
                'owner': owners[0],  # Jody (index 0)
            },
        ]

        leads = []
        for data in leads_data:
            lead = Lead.objects.create(
                **{k: v for k, v in data.items() if k != 'owner'},
                country=self.country_usa,
                lead_source=self.lead_source_website,
                type=self.client_type_end_customer,
                department=department,
            )
            lead.industry.add(self.industry_tech)
            leads.append(lead)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(leads)} leads'))
        return leads

