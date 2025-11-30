"""
Management command to create default products for 3 pillars.
Creates micro-sites as the default product.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from common.models import Product


class Command(BaseCommand):
    help = 'Create default products for 3 pillars (micro-sites, etc.)'

    def handle(self, *args, **options):
        # Create micro-sites product (default)
        product, created = Product.objects.get_or_create(
            slug='micro-sites',
            defaults={
                'name': 'Micro-sites',
                'description': 'Custom micro-site development and hosting',
                'pillar': 'development',
                'is_active': True,
                'is_default': True,
                'order': 1,
                'price': 2500.00,  # Default price R 2500
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created product: {product.name}')
            )
        else:
            # Update to ensure it's default and has price
            product.is_default = True
            product.is_active = True
            if not product.price or product.price == 0:
                product.price = 2500.00
            product.save()
            self.stdout.write(
                self.style.SUCCESS(f'Product already exists: {product.name} (updated to default)')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Default product: {product.name} (ID: {product.id})')
        )

