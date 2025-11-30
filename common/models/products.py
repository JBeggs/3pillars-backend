"""
Product model for 3 pillars business offerings.
Products are services offered by the business (micro-sites, etc.)

This model is in a separate file but imported in common/models.py
so Django can discover it properly.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """
    Product model for 3 pillars offerings.
    Examples: micro-sites, web development, technical support, etc.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name=_("Product Name"),
        help_text=_("Name of the product/service")
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly identifier")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Product description")
    )
    pillar = models.CharField(
        max_length=50,
        choices=[
            ('project_management', 'Project/Task Management'),
            ('technical_sales', 'Technical and Sales'),
            ('development', 'Development'),
        ],
        verbose_name=_("Pillar"),
        help_text=_("Which pillar this product belongs to")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this product is currently available")
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default Product"),
        help_text=_("Default product for new registrations")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("Order in which products are displayed")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one default product
        if self.is_default:
            Product.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

