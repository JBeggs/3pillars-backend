"""
Multi-tenant e-commerce models for product management.
Based on JavaMellow Backend API Specification.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class EcommerceCompany(models.Model):
    """
    Multi-tenant company/organization model.
    Each company has isolated product data.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
        ('cancelled', 'Cancelled'),
    ]
    
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    # Core Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    
    # Basic Information
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Address
    address_street = models.CharField(max_length=255, blank=True, null=True)
    address_city = models.CharField(max_length=100, blank=True, null=True)
    address_province = models.CharField(max_length=100, blank=True, null=True)
    address_postal_code = models.CharField(max_length=20, blank=True, null=True)
    address_country = models.CharField(max_length=2, default='ZA')  # ISO country code
    
    # Business Details
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Branding
    logo = models.URLField(blank=True, null=True)
    brand_color = models.CharField(max_length=7, blank=True, null=True)  # Hex color
    
    # Settings
    currency = models.CharField(max_length=3, default='ZAR')
    timezone = models.CharField(max_length=50, default='Africa/Johannesburg')
    language = models.CharField(max_length=10, default='en')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    
    # Limits (based on plan)
    max_products = models.IntegerField(null=True, blank=True)  # null = unlimited
    max_storage_gb = models.IntegerField(null=True, blank=True)
    max_users = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trial_ends_at = models.DateTimeField(blank=True, null=True)
    
    # Owner/Admin user
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ecommerce_companies')
    
    # Users who are members of this company (many-to-many for future expansion)
    users = models.ManyToManyField(
        User,
        related_name='member_companies',
        blank=True,
        help_text='Users who are members of this company (in addition to owner)'
    )
    
    # Product selection (from 3 pillars products)
    product = models.ForeignKey(
        'common.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies',
        help_text='Product/service selected during registration',
        verbose_name=_("Product")
    )
    
    # Registration deal (deal created for this company registration)
    registration_deal = models.ForeignKey(
        'crm.Deal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_companies',
        help_text='Deal created for this company registration'
    )
    
    class Meta:
        verbose_name = _('E-commerce Company')
        verbose_name_plural = _('E-commerce Companies')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['plan']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.slug:
            # Ensure slug is lowercase and hyphenated
            self.slug = self.slug.lower().replace('_', '-')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Product categories - scoped to company.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(EcommerceCompany, on_delete=models.CASCADE, related_name='categories')
    slug = models.SlugField(max_length=255, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        unique_together = [['company', 'slug']]
        indexes = [
            models.Index(fields=['company', 'slug']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class EcommerceProduct(models.Model):
    """
    Multi-tenant product model.
    Products are scoped to companies - each company has isolated product data.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]
    
    # Core Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(EcommerceCompany, on_delete=models.CASCADE, related_name='products', db_index=True)
    slug = models.SlugField(max_length=255, db_index=True)
    
    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(validators=[MaxLengthValidator(2000)])
    short_description = models.CharField(max_length=150, blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Visual
    image = models.URLField()  # Main product image
    images = models.JSONField(default=list, blank=True)  # Additional images array
    color = models.CharField(max_length=50, blank=True, null=True)  # Tailwind color class
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    tags = models.JSONField(default=list, blank=True)  # Array of tag strings
    
    # Inventory
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(null=True, blank=True)  # null = unlimited
    sku = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    track_inventory = models.BooleanField(default=False)
    
    # Status & Visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    
    # SEO
    seo_title = models.CharField(max_length=60, blank=True, null=True)
    seo_description = models.CharField(max_length=160, blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    canonical_url = models.URLField(blank=True, null=True)
    
    # Metadata
    weight = models.IntegerField(null=True, blank=True)  # grams
    dimension_length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # cm
    dimension_width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # cm
    dimension_height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # cm
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('E-commerce Product')
        verbose_name_plural = _('E-commerce Products')
        unique_together = [['company', 'slug']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'slug']),
            models.Index(fields=['company', 'category']),
            models.Index(fields=['company', 'status', 'in_stock']),
            models.Index(fields=['company', 'sku']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"
    
    def clean(self):
        if self.compare_at_price and self.price:
            if self.compare_at_price < self.price:
                raise ValidationError({'compare_at_price': 'Compare at price must be greater than or equal to price'})
        
        if self.slug:
            # Ensure slug is lowercase and hyphenated
            self.slug = self.slug.lower().replace('_', '-')
    
    def save(self, *args, **kwargs):
        # Auto-set published_at when status changes to active
        if self.status == 'active' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        self.full_clean()
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """
    Product images with company organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(EcommerceCompany, on_delete=models.CASCADE, related_name='product_images', db_index=True)
    product = models.ForeignKey(EcommerceProduct, on_delete=models.CASCADE, related_name='product_image_objects', null=True, blank=True)
    
    url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True)
    filename = models.CharField(max_length=255)
    size = models.IntegerField()  # bytes
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        indexes = [
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        return self.filename


class Cart(models.Model):
    """
    Multi-tenant shopping cart model.
    Carts are scoped to companies - each company has isolated cart data.
    """
    DELIVERY_METHOD_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('same-day', 'Same Day'),
        ('pudo', 'Pudo Pickup Point'),
    ]
    
    # Core Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(EcommerceCompany, on_delete=models.CASCADE, related_name='carts', db_index=True)
    session_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')
    
    # Pricing Summary
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Shipping Information (JSON field for flexibility)
    shipping_address = models.JSONField(default=dict, blank=True)
    
    # Delivery Method
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, blank=True, null=True)
    
    # Pudo Pickup Point (JSON field)
    pudo_pickup_point = models.JSONField(default=dict, blank=True)
    
    # Discount Code
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Metadata
    currency = models.CharField(max_length=3, default='ZAR')
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        unique_together = [['company', 'session_id']]
        indexes = [
            models.Index(fields=['company', 'session_id']),
            models.Index(fields=['company', 'user']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - Cart {self.id}"
    
    def calculate_totals(self):
        """Calculate cart totals."""
        from decimal import Decimal
        from django.utils import timezone
        
        # Calculate subtotal from items
        self.subtotal = sum(item.subtotal for item in self.items.all())
        
        # Calculate shipping
        self.shipping = self._calculate_shipping()
        
        # Calculate tax (15% VAT for South Africa)
        self.tax = (self.subtotal - self.discount) * Decimal('0.15')
        
        # Calculate total
        self.total = self.subtotal + self.shipping + self.tax - self.discount
        
        # Set expiration (30 days from last update)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        else:
            # Extend expiration on update
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
    
    def _calculate_shipping(self):
        """Calculate shipping cost based on subtotal and delivery method."""
        from decimal import Decimal
        
        FREE_SHIPPING_THRESHOLD = Decimal('200.00')
        
        if self.subtotal >= FREE_SHIPPING_THRESHOLD and self.delivery_method == 'standard':
            return Decimal('0.00')
        
        rates = {
            'standard': Decimal('50.00'),
            'express': Decimal('100.00'),
            'same-day': Decimal('150.00'),
            'pudo': Decimal('40.00'),
        }
        
        return rates.get(self.delivery_method, Decimal('50.00'))


class CartItem(models.Model):
    """
    Cart item model - products in a cart.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(EcommerceProduct, on_delete=models.CASCADE, related_name='cart_items')
    
    # Snapshot data (in case product changes)
    product_name = models.CharField(max_length=200)
    product_image = models.URLField()
    product_sku = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = [['cart', 'product']]
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.cart} - {self.product_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate subtotal before saving."""
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


class Order(models.Model):
    """
    Multi-tenant order model.
    Orders are scoped to companies - each company has isolated order data.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('yoco', 'Yoco'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('same-day', 'Same Day'),
        ('pudo', 'Pudo Pickup Point'),
    ]
    
    # Core Identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, db_index=True)
    company = models.ForeignKey(EcommerceCompany, on_delete=models.CASCADE, related_name='orders', db_index=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    session_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    
    # Order Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    shipping = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='yoco')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    yoco_checkout_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    yoco_payment_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Customer Information (snapshot)
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50, blank=True, null=True)
    
    # Shipping Information (JSON field)
    shipping_address = models.JSONField()
    
    # Delivery
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    
    # Pudo Pickup Point (JSON field)
    pudo_pickup_point = models.JSONField(default=dict, blank=True)
    
    # Courier Information (JSON field)
    courier = models.JSONField(default=dict, blank=True)
    waybill_number = models.CharField(max_length=255, blank=True, null=True)
    collection_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Metadata
    currency = models.CharField(max_length=3, default='ZAR')
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        unique_together = [['company', 'order_number']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'order_number']),
            models.Index(fields=['company', 'customer']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['company', 'created_at']),
            models.Index(fields=['yoco_checkout_id']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.order_number}"


class CompanyIntegrationSettings(models.Model):
    """
    Company-specific integration settings for payment gateways and courier services.
    Each company has their own API keys and credentials.
    """
    PAYMENT_GATEWAY_CHOICES = [
        ('yoco', 'Yoco'),
        ('payfast', 'PayFast'),
        ('paystack', 'PayStack'),
        ('stripe', 'Stripe'),
        # Add more as needed
    ]
    
    COURIER_CHOICES = [
        ('courier_guy', 'The Courier Guy'),
        ('pudo', 'Pudo (via Courier Guy)'),
        ('fastway', 'Fastway'),
        ('postnet', 'PostNet'),
        # Add more as needed
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(
        EcommerceCompany,
        on_delete=models.CASCADE,
        related_name='integration_settings'
    )
    
    # Payment Gateway Settings
    payment_gateway = models.CharField(
        max_length=50,
        choices=PAYMENT_GATEWAY_CHOICES,
        default='yoco',
        help_text='Primary payment gateway'
    )
    
    # Yoco Settings
    yoco_secret_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Yoco secret key (stored encrypted in production)'
    )
    yoco_public_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Yoco public key'
    )
    yoco_webhook_secret = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Yoco webhook secret for signature verification'
    )
    yoco_sandbox_mode = models.BooleanField(
        default=True,
        help_text='Use Yoco sandbox/test mode'
    )
    
    # Courier Guy Settings
    courier_service = models.CharField(
        max_length=50,
        choices=COURIER_CHOICES,
        default='courier_guy',
        help_text='Primary courier service'
    )
    courier_guy_api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='The Courier Guy API key'
    )
    courier_guy_api_secret = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='The Courier Guy API secret'
    )
    courier_guy_account_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='The Courier Guy account number'
    )
    courier_guy_sandbox_mode = models.BooleanField(
        default=True,
        help_text='Use Courier Guy sandbox/test mode'
    )
    
    # Additional payment gateway settings (JSON field for flexibility)
    payment_gateway_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional payment gateway settings (for future gateways)'
    )
    
    # Additional courier settings (JSON field for flexibility)
    courier_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional courier service settings (for future couriers)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Company Integration Settings')
        verbose_name_plural = _('Company Integration Settings')
    
    def __str__(self):
        return f"Integration Settings - {self.company.name}"
    
    def get_yoco_credentials(self):
        """Get Yoco credentials for API calls."""
        return {
            'secret_key': self.yoco_secret_key,
            'public_key': self.yoco_public_key,
            'webhook_secret': self.yoco_webhook_secret,
            'sandbox_mode': self.yoco_sandbox_mode,
        }
    
    def get_courier_guy_credentials(self):
        """Get Courier Guy credentials for API calls."""
        return {
            'api_key': self.courier_guy_api_key,
            'api_secret': self.courier_guy_api_secret,
            'account_number': self.courier_guy_account_number,
            'sandbox_mode': self.courier_guy_sandbox_mode,
        }
    
    def generate_order_number(self):
        """Generate unique order number for company."""
        from django.utils import timezone
        year = timezone.now().year
        # Get sequence number for this company and year
        last_order = Order.objects.filter(
            company=self.company,
            order_number__startswith=f"ORD-{year}-"
        ).order_by('-order_number').first()
        
        if last_order:
            try:
                sequence = int(last_order.order_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                sequence = 1
        else:
            sequence = 1
        
        return f"ORD-{year}-{sequence:04d}"
    
    def save(self, *args, **kwargs):
        """Generate order number if not set."""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Order item model - products in an order (snapshot at time of order).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(EcommerceProduct, on_delete=models.PROTECT, related_name='order_items')
    
    # Snapshot data (product may change after order)
    product_name = models.CharField(max_length=200)
    product_image = models.URLField()
    product_sku = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate subtotal before saving."""
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

