"""
Serializers for e-commerce multi-tenant API.
"""
from rest_framework import serializers
from .models import (
    EcommerceCompany, EcommerceProduct, Category, ProductImage,
    Cart, CartItem, Order, OrderItem, CompanyIntegrationSettings
)


class EcommerceCompanySerializer(serializers.ModelSerializer):
    """Serializer for E-commerce Company."""
    
    class Meta:
        model = EcommerceCompany
        fields = [
            'id', 'slug', 'name', 'legal_name', 'description',
            'email', 'phone', 'website',
            'address_street', 'address_city', 'address_province', 
            'address_postal_code', 'address_country',
            'registration_number', 'tax_number',
            'logo', 'brand_color',
            'currency', 'timezone', 'language',
            'status', 'plan',
            'max_products', 'max_storage_gb', 'max_users',
            'created_at', 'updated_at', 'trial_ends_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_slug(self, value):
        """Ensure slug is lowercase and hyphenated."""
        return value.lower().replace('_', '-')


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category."""
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'company', 'slug', 'name', 'description', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_product_count(self, obj):
        return obj.products.count()
    
    def create(self, validated_data):
        """Create category with auto-generated slug if not provided."""
        from django.utils.text import slugify
        
        if 'slug' not in validated_data or not validated_data.get('slug'):
            name = validated_data.get('name', '')
            if name:
                base_slug = slugify(name)
                slug = base_slug
                # Ensure uniqueness within company
                company = validated_data.get('company')
                counter = 1
                while Category.objects.filter(company=company, slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                validated_data['slug'] = slug
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update category, auto-generate slug if name changed and slug not provided."""
        from django.utils.text import slugify
        
        # If name changed and slug not explicitly provided, regenerate slug
        if 'name' in validated_data and 'slug' not in validated_data:
            new_name = validated_data['name']
            if new_name != instance.name:
                base_slug = slugify(new_name)
                slug = base_slug
                # Ensure uniqueness within company
                company = instance.company
                counter = 1
                while Category.objects.filter(company=company, slug=slug).exclude(id=instance.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                validated_data['slug'] = slug
        
        return super().update(instance, validated_data)


class EcommerceProductSerializer(serializers.ModelSerializer):
    """Serializer for E-commerce Product."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = EcommerceProduct
        fields = [
            'id', 'company', 'company_name', 'slug', 'name', 'description', 'short_description',
            'price', 'compare_at_price', 'cost_price',
            'image', 'images', 'color',
            'category', 'category_name', 'category_slug', 'tags',
            'in_stock', 'stock_quantity', 'sku', 'track_inventory',
            'status', 'featured',
            'seo_title', 'seo_description', 'seo_keywords', 'canonical_url',
            'weight', 'dimension_length', 'dimension_width', 'dimension_height',
            'created_at', 'updated_at', 'published_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at']
    
    def validate(self, data):
        """Validate product data."""
        compare_at_price = data.get('compare_at_price')
        price = data.get('price', self.instance.price if self.instance else None)
        
        if compare_at_price and price:
            if compare_at_price < price:
                raise serializers.ValidationError({
                    'compare_at_price': 'Compare at price must be greater than or equal to price'
                })
        
        return data
    
    def validate_slug(self, value):
        """Ensure slug is lowercase and hyphenated."""
        if value:
            return value.lower().replace('_', '-')
        return value
    
    def create(self, validated_data):
        """Create product with auto-generated slug if not provided."""
        from django.utils.text import slugify
        
        if 'slug' not in validated_data or not validated_data.get('slug'):
            name = validated_data.get('name', '')
            if name:
                base_slug = slugify(name)
                slug = base_slug
                # Ensure uniqueness within company
                company = validated_data.get('company')
                counter = 1
                while EcommerceProduct.objects.filter(company=company, slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                validated_data['slug'] = slug
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update product, auto-generate slug if name changed and slug not provided."""
        from django.utils.text import slugify
        
        # If name changed and slug not explicitly provided, regenerate slug
        if 'name' in validated_data and 'slug' not in validated_data:
            new_name = validated_data['name']
            if new_name != instance.name:
                base_slug = slugify(new_name)
                slug = base_slug
                # Ensure uniqueness within company
                company = instance.company
                counter = 1
                while EcommerceProduct.objects.filter(company=company, slug=slug).exclude(id=instance.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                validated_data['slug'] = slug
        
        return super().update(instance, validated_data)


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for Product Image."""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'company', 'product', 'url', 'thumbnail_url',
            'filename', 'size', 'width', 'height', 'mime_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BulkOperationSerializer(serializers.Serializer):
    """Serializer for bulk operations."""
    operation = serializers.ChoiceField(choices=['update', 'delete', 'archive'])
    ids = serializers.ListField(child=serializers.UUIDField())
    data = serializers.DictField(required=False)


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for Cart Item."""
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product_id', 'product', 'product_name', 'product_image',
            'product_sku', 'price', 'quantity', 'subtotal',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'product_name', 'product_image', 'product_sku', 'price', 'subtotal', 'created_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart."""
    items = CartItemSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'company', 'company_name', 'session_id', 'user',
            'items', 'subtotal', 'shipping', 'tax', 'discount', 'total',
            'shipping_address', 'delivery_method', 'pudo_pickup_point',
            'discount_code', 'currency', 'expires_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'subtotal', 'shipping', 'tax', 'total', 'created_at', 'updated_at', 'expires_at']


class AddCartItemSerializer(serializers.Serializer):
    """Serializer for adding item to cart."""
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=100)


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    quantity = serializers.IntegerField(min_value=1, max_value=100)


class UpdateShippingSerializer(serializers.Serializer):
    """Serializer for updating cart shipping information."""
    shipping_address = serializers.DictField(required=False)
    delivery_method = serializers.ChoiceField(
        choices=['standard', 'express', 'same-day', 'pudo'],
        required=False
    )
    pudo_pickup_point = serializers.DictField(required=False)


class ApplyDiscountSerializer(serializers.Serializer):
    """Serializer for applying discount code."""
    code = serializers.CharField(max_length=50)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for Order Item."""
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product', 'product_name', 'product_image',
            'product_sku', 'price', 'quantity', 'subtotal', 'created_at'
        ]
        read_only_fields = ['id', 'product_name', 'product_image', 'product_sku', 'price', 'subtotal', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order."""
    items = OrderItemSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'company', 'company_name', 'customer', 'session_id',
            'status', 'items', 'subtotal', 'shipping', 'tax', 'discount', 'total',
            'payment_method', 'payment_status', 'yoco_checkout_id', 'yoco_payment_id',
            'transaction_id', 'customer_first_name', 'customer_last_name',
            'customer_email', 'customer_phone', 'shipping_address', 'delivery_method',
            'estimated_delivery', 'tracking_number', 'pudo_pickup_point', 'courier',
            'waybill_number', 'collection_code', 'currency', 'notes',
            'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at', 'cancelled_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'shipping', 'tax', 'total',
            'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at', 'cancelled_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating order from cart."""
    customer = serializers.DictField()
    shipping_address = serializers.DictField()
    delivery_method = serializers.ChoiceField(choices=['standard', 'express', 'same-day', 'pudo'])
    pudo_pickup_point = serializers.DictField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Serializer for updating order status."""
    status = serializers.ChoiceField(choices=['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'])
    notes = serializers.CharField(required=False, allow_blank=True)


class UpdatePaymentSerializer(serializers.Serializer):
    """Serializer for updating payment information."""
    payment = serializers.DictField()
    status = serializers.ChoiceField(choices=['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'])


class UpdateTrackingSerializer(serializers.Serializer):
    """Serializer for updating tracking information."""
    tracking_number = serializers.CharField(required=False, allow_blank=True)
    waybill_number = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=['shipped', 'delivered'], required=False)
    shipped_at = serializers.DateTimeField(required=False)
    estimated_delivery = serializers.DateTimeField(required=False)
    courier = serializers.DictField(required=False)
    pudo_pickup_point = serializers.DictField(required=False)
    collection_code = serializers.CharField(required=False, allow_blank=True)


class CancelOrderSerializer(serializers.Serializer):
    """Serializer for cancelling order."""
    reason = serializers.CharField()
    refund = serializers.BooleanField(default=False)


class YocoCheckoutSerializer(serializers.Serializer):
    """Serializer for creating Yoco checkout session."""
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class PudoLocationSerializer(serializers.Serializer):
    """Serializer for Pudo location (external API response)."""
    id = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    province = serializers.CharField()
    country = serializers.CharField(default='ZA')
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    distance = serializers.FloatField(required=False)
    operating_hours = serializers.DictField(required=False)
    contact = serializers.DictField(required=False)
    features = serializers.ListField(child=serializers.CharField(), required=False)


class PudoShipmentSerializer(serializers.Serializer):
    """Serializer for creating Pudo shipment."""
    pudo_pickup_point_id = serializers.CharField()
    parcel_description = serializers.CharField()
    parcel_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    parcel_weight = serializers.DecimalField(max_digits=8, decimal_places=2)


class CompanyIntegrationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for Company Integration Settings."""
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = CompanyIntegrationSettings
        fields = [
            'id', 'company', 'company_name',
            'payment_gateway',
            'yoco_secret_key', 'yoco_public_key', 'yoco_webhook_secret', 'yoco_sandbox_mode',
            'courier_service',
            'courier_guy_api_key', 'courier_guy_api_secret', 'courier_guy_account_number', 'courier_guy_sandbox_mode',
            'payment_gateway_settings', 'courier_settings',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']
        extra_kwargs = {
            'yoco_secret_key': {'write_only': False},  # Allow reading for display (masked on frontend)
            'yoco_webhook_secret': {'write_only': False},
            'courier_guy_api_secret': {'write_only': False},
        }
    
    def to_representation(self, instance):
        """Mask sensitive fields when reading."""
        data = super().to_representation(instance)
        
        # Mask secret keys (show only last 4 characters)
        if data.get('yoco_secret_key'):
            data['yoco_secret_key'] = self._mask_secret(data['yoco_secret_key'])
        if data.get('yoco_webhook_secret'):
            data['yoco_webhook_secret'] = self._mask_secret(data['yoco_webhook_secret'])
        if data.get('courier_guy_api_secret'):
            data['courier_guy_api_secret'] = self._mask_secret(data['courier_guy_api_secret'])
        
        return data
    
    def _mask_secret(self, value):
        """Mask secret value, showing only last 4 characters."""
        if not value or len(value) <= 4:
            return '••••'
        return '•' * (len(value) - 4) + value[-4:]
    
    def validate(self, data):
        """Validate integration settings."""
        # If updating secret keys, check if they're masked (user didn't change them)
        # In that case, don't update them
        if self.instance:
            # Check if secret keys are masked (starts with •)
            if 'yoco_secret_key' in data and data['yoco_secret_key'].startswith('•'):
                data.pop('yoco_secret_key')  # Don't update if masked
            if 'yoco_webhook_secret' in data and data['yoco_webhook_secret'].startswith('•'):
                data.pop('yoco_webhook_secret')
            if 'courier_guy_api_secret' in data and data['courier_guy_api_secret'].startswith('•'):
                data.pop('courier_guy_api_secret')
        
        return data

