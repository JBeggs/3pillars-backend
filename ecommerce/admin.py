from django.contrib import admin
from .models import (
    EcommerceCompany, EcommerceProduct, Category, ProductImage,
    Cart, CartItem, Order, OrderItem, CompanyIntegrationSettings
)


@admin.register(EcommerceCompany)
class EcommerceCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'email', 'status', 'plan', 'created_at']
    list_filter = ['status', 'plan', 'created_at']
    search_fields = ['name', 'email', 'slug']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'slug', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(EcommerceProduct)
class EcommerceProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'category', 'price', 'status', 'in_stock', 'created_at']
    list_filter = ['company', 'status', 'featured', 'in_stock', 'category', 'created_at']
    search_fields = ['name', 'description', 'sku', 'slug']
    readonly_fields = ['id', 'created_at', 'updated_at', 'published_at']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['filename', 'company', 'product', 'size', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['filename', 'url']
    readonly_fields = ['id', 'created_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'user', 'total', 'item_count', 'created_at']
    list_filter = ['company', 'delivery_method', 'created_at']
    search_fields = ['session_id', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'expires_at']
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'cart', 'quantity', 'price', 'subtotal']
    list_filter = ['cart__company', 'created_at']
    search_fields = ['product_name', 'product_sku']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'company', 'customer_email', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['company', 'status', 'payment_status', 'delivery_method', 'created_at']
    search_fields = ['order_number', 'customer_email', 'customer_first_name', 'customer_last_name']
    readonly_fields = ['id', 'order_number', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at', 'cancelled_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'order', 'quantity', 'price', 'subtotal']
    list_filter = ['order__company', 'created_at']
    search_fields = ['product_name', 'product_sku']
    readonly_fields = ['id', 'created_at']


@admin.register(CompanyIntegrationSettings)
class CompanyIntegrationSettingsAdmin(admin.ModelAdmin):
    list_display = ['company', 'payment_gateway', 'courier_service', 'yoco_sandbox_mode', 'courier_guy_sandbox_mode', 'updated_at']
    list_filter = ['payment_gateway', 'courier_service', 'yoco_sandbox_mode', 'courier_guy_sandbox_mode']
    search_fields = ['company__name', 'company__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['company']
    
    fieldsets = (
        ('Company', {
            'fields': ('company',)
        }),
        ('Payment Gateway', {
            'fields': ('payment_gateway',)
        }),
        ('Yoco Settings', {
            'fields': (
                'yoco_secret_key',
                'yoco_public_key',
                'yoco_webhook_secret',
                'yoco_sandbox_mode',
            ),
            'classes': ('collapse',)
        }),
        ('Courier Service', {
            'fields': ('courier_service',)
        }),
        ('Courier Guy Settings', {
            'fields': (
                'courier_guy_api_key',
                'courier_guy_api_secret',
                'courier_guy_account_number',
                'courier_guy_sandbox_mode',
            ),
            'classes': ('collapse',)
        }),
        ('Additional Settings', {
            'fields': ('payment_gateway_settings', 'courier_settings'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

