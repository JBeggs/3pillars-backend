"""
Management command to create sample articles for Riverside Herald.
Creates 3 initial articles with proper content and metadata.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from ecommerce.models import EcommerceCompany
from news.models import Article

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample articles for Riverside Herald"

    def add_arguments(self, parser):
        parser.add_argument(
            '--company-name',
            type=str,
            default='Riverside Herald',
            help='Company name (default: Riverside Herald)',
        )
        parser.add_argument(
            '--author-email',
            type=str,
            default='jody@riversideherald.co.za',
            help='Author email address (default: jody@riversideherald.co.za)',
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['draft', 'published', 'scheduled', 'archived', 'featured'],
            default='published',
            help='Article status (default: published)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        company_name = options['company_name']
        author_email = options['author_email']
        status = options['status']

        self.stdout.write(self.style.SUCCESS('Creating sample articles...'))

        # Find Riverside Herald company
        company = None
        for name_variant in [company_name, 'riverside-herald', 'riversideherald']:
            company = EcommerceCompany.objects.filter(
                name__iexact=name_variant
            ).first() or EcommerceCompany.objects.filter(
                slug__iexact=slugify(name_variant)
            ).first()
            if company:
                break

        if not company:
            self.stdout.write(self.style.ERROR(
                f'Company "{company_name}" not found. Please create it first using create_riverside_herald_user command.'
            ))
            return

        self.stdout.write(self.style.SUCCESS(f'✓ Found company: {company.name} (ID: {company.id})'))

        # Find author user
        author = User.objects.filter(email=author_email).first()
        if not author:
            # Try username
            username = author_email.split('@')[0]
            author = User.objects.filter(username=username).first()
        
        if not author:
            self.stdout.write(self.style.ERROR(
                f'Author user with email "{author_email}" not found. Please create it first.'
            ))
            return

        self.stdout.write(self.style.SUCCESS(f'✓ Found author: {author.email} ({author.username})'))

        # Article 1: Riverside Lodge Opening
        article1_data = {
            'title': 'Riverside Lodge Opening',
            'subtitle': 'Grand Opening Celebration Marks New Era for Local Hospitality',
            'excerpt': 'Riverside Lodge officially opens its doors, bringing luxury accommodation and world-class service to the community.',
            'content': '''<h2>Riverside Lodge Grand Opening</h2>
<p>We are thrilled to announce the grand opening of Riverside Lodge, a premier destination for travelers seeking comfort, elegance, and exceptional service. Located in the heart of our beautiful region, Riverside Lodge represents a new standard in hospitality.</p>

<h3>What to Expect</h3>
<p>The lodge features:</p>
<ul>
    <li>Luxurious accommodation with stunning river views</li>
    <li>World-class dining facilities</li>
    <li>State-of-the-art conference and event spaces</li>
    <li>Recreational facilities including spa and wellness center</li>
    <li>Eco-friendly practices and sustainable tourism initiatives</li>
</ul>

<h3>Grand Opening Events</h3>
<p>Join us for a series of special events celebrating our opening:</p>
<ul>
    <li>Opening ceremony with local dignitaries</li>
    <li>Guided tours of the facilities</li>
    <li>Complimentary refreshments and entertainment</li>
    <li>Special introductory rates for early bookings</li>
</ul>

<p>Riverside Lodge is committed to providing an unforgettable experience for every guest. We look forward to welcoming you soon!</p>

<p><strong>Contact Information:</strong><br>
Email: info@riversidelodge.co.za<br>
Phone: +27 (0)XX XXX XXXX<br>
Address: [Address to be added]</p>''',
            'status': status,
            'is_breaking_news': False,
            'is_trending': True,
            'is_premium': False,
            'published_at': timezone.now() if status == 'published' else None,
        }

        # Article 2: 3 Pillars Management System
        article2_data = {
            'title': '3 Pillars Management and Social Media System Starts Operating',
            'subtitle': 'Revolutionary Business Management Platform Launches to Transform Local Operations',
            'excerpt': 'The new 3 Pillars management and social media system is now operational, offering comprehensive business solutions for local enterprises.',
            'content': '''<h2>3 Pillars Management System Launch</h2>
<p>We are excited to announce that the 3 Pillars Management and Social Media System is now fully operational and ready to transform how local businesses operate and engage with their customers.</p>

<h3>What is 3 Pillars?</h3>
<p>The 3 Pillars system is a comprehensive business management platform that combines:</p>
<ul>
    <li><strong>Project & Task Management:</strong> Streamline your operations with powerful project tracking and task management tools</li>
    <li><strong>Technical Sales & CRM:</strong> Manage customer relationships, deals, and sales pipelines effectively</li>
    <li><strong>Development Services:</strong> Access professional development resources and technical support</li>
</ul>

<h3>Social Media Integration</h3>
<p>Our integrated social media management system allows businesses to:</p>
<ul>
    <li>Schedule and publish content across multiple platforms</li>
    <li>Monitor social media engagement and analytics</li>
    <li>Manage customer interactions and responses</li>
    <li>Track social media campaign performance</li>
</ul>

<h3>Key Features</h3>
<ul>
    <li>Multi-tenant architecture for secure business isolation</li>
    <li>Real-time collaboration tools</li>
    <li>Comprehensive reporting and analytics</li>
    <li>Mobile app access for on-the-go management</li>
    <li>Customizable workflows to fit your business needs</li>
</ul>

<h3>Getting Started</h3>
<p>Businesses interested in using the 3 Pillars system can:</p>
<ul>
    <li>Register through our online portal</li>
    <li>Contact our sales team for a personalized demonstration</li>
    <li>Access free resources and documentation</li>
</ul>

<p>The system is designed to scale with your business, from small startups to large enterprises. Join us in revolutionizing business management!</p>

<p><strong>Learn More:</strong><br>
Visit: https://3pillars.pythonanywhere.com<br>
Email: info@3pillars.co.za</p>''',
            'status': status,
            'is_breaking_news': True,
            'is_trending': True,
            'is_premium': False,
            'published_at': timezone.now() if status == 'published' else None,
        }

        # Article 3: Business Registration Welcome
        article3_data = {
            'title': 'Business Welcome to Register to Riverside Herald as Authors, Business',
            'subtitle': 'Join Riverside Herald: Share Your Business Story and Connect with the Community',
            'excerpt': 'Riverside Herald invites local businesses to register and become content authors, sharing their stories and connecting with our community.',
            'content': '''<h2>Welcome to Riverside Herald</h2>
<p>Riverside Herald is excited to welcome local businesses to our platform! We're opening our doors to businesses who want to share their stories, connect with the community, and grow their presence online.</p>

<h3>Why Register as a Business Author?</h3>
<p>By registering with Riverside Herald, your business can:</p>
<ul>
    <li><strong>Publish Content:</strong> Share news, updates, and stories about your business</li>
    <li><strong>Build Your Brand:</strong> Establish your business as a thought leader in your industry</li>
    <li><strong>Connect with Customers:</strong> Engage directly with the community and potential customers</li>
    <li><strong>Increase Visibility:</strong> Reach a wider audience through our platform</li>
    <li><strong>Network Opportunities:</strong> Connect with other local businesses and partners</li>
</ul>

<h3>What You Can Do</h3>
<p>As a registered business author, you'll have access to:</p>
<ul>
    <li>Content creation and publishing tools</li>
    <li>Business directory listing</li>
    <li>Media gallery for your business images</li>
    <li>Analytics to track your content performance</li>
    <li>Customer review and feedback system</li>
</ul>

<h3>Registration Process</h3>
<p>Getting started is easy:</p>
<ol>
    <li><strong>Sign Up:</strong> Create your business account on Riverside Herald</li>
    <li><strong>Verify Your Business:</strong> Complete your business profile with accurate information</li>
    <li><strong>Get Approved:</strong> Our team will review and approve your registration</li>
    <li><strong>Start Publishing:</strong> Begin creating and sharing your content!</li>
</ol>

<h3>Content Guidelines</h3>
<p>We encourage businesses to share:</p>
<ul>
    <li>Company news and announcements</li>
    <li>Product launches and updates</li>
    <li>Industry insights and expertise</li>
    <li>Community involvement and events</li>
    <li>Customer success stories</li>
</ul>

<h3>Join Us Today</h3>
<p>Don't miss out on this opportunity to grow your business presence and connect with the Riverside Herald community. Register today and start sharing your story!</p>

<p><strong>Ready to Get Started?</strong><br>
Visit our registration page or contact us:<br>
Email: business@riversideherald.co.za<br>
Phone: [Contact number to be added]</p>

<p>We look forward to welcoming you to the Riverside Herald family!</p>''',
            'status': status,
            'is_breaking_news': False,
            'is_trending': True,
            'is_premium': False,
            'published_at': timezone.now() if status == 'published' else None,
        }

        articles_data = [
            ('Riverside Lodge Opening', article1_data),
            ('3 Pillars Management and Social Media System Starts Operating', article2_data),
            ('Business Welcome to Register to Riverside Herald as Authors, Business', article3_data),
        ]

        created_count = 0
        updated_count = 0

        for title, article_data in articles_data:
            # Generate slug from title
            slug = slugify(title)
            
            # Check if article already exists
            article, created = Article.objects.get_or_create(
                company=company,
                slug=slug,
                defaults={
                    'title': article_data['title'],
                    'subtitle': article_data['subtitle'],
                    'excerpt': article_data['excerpt'],
                    'content': article_data['content'],
                    'author': author,
                    'status': article_data['status'],
                    'is_breaking_news': article_data['is_breaking_news'],
                    'is_trending': article_data['is_trending'],
                    'is_premium': article_data['is_premium'],
                    'published_at': article_data['published_at'],
                    'seo_title': article_data['title'],
                    'seo_description': article_data['excerpt'],
                }
            )

            if not created:
                # Update existing article
                article.title = article_data['title']
                article.subtitle = article_data['subtitle']
                article.excerpt = article_data['excerpt']
                article.content = article_data['content']
                article.author = author
                article.status = article_data['status']
                article.is_breaking_news = article_data['is_breaking_news']
                article.is_trending = article_data['is_trending']
                article.is_premium = article_data['is_premium']
                article.published_at = article_data['published_at']
                article.seo_title = article_data['title']
                article.seo_description = article_data['excerpt']
                article.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'  Updated: {title}'))
            else:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {title}'))

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✅ Complete!'))
        self.stdout.write(f'  Created: {created_count} articles')
        self.stdout.write(f'  Updated: {updated_count} articles')
        self.stdout.write(f'  Company: {company.name}')
        self.stdout.write(f'  Author: {author.email}')
        self.stdout.write(f'  Status: {status}')
        
        if status == 'published':
            self.stdout.write(self.style.SUCCESS('\n📰 Articles are now live and visible to readers!'))

