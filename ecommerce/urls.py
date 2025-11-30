"""
URL configuration for e-commerce API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EcommerceCompanyViewSet,
    EcommerceProductViewSet,
    CategoryViewSet,
    ProductImageViewSet,
)
from .views_cart import CartViewSet
from .views_orders import OrderViewSet
from .views_pudo import PudoViewSet, PudoShipmentViewSet
from .views_yoco import YocoViewSet, YocoWebhookViewSet
from .views_analytics import SalesAnalyticsViewSet

router = DefaultRouter()
router.register(r'companies', EcommerceCompanyViewSet, basename='ecommerce-company')
router.register(r'products', EcommerceProductViewSet, basename='ecommerce-product')
router.register(r'categories', CategoryViewSet, basename='ecommerce-category')
router.register(r'products/images', ProductImageViewSet, basename='product-image')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'pudo', PudoViewSet, basename='pudo')
router.register(r'pudo-shipments', PudoShipmentViewSet, basename='pudo-shipment')
router.register(r'yoco', YocoViewSet, basename='yoco')
router.register(r'yoco-webhooks', YocoWebhookViewSet, basename='yoco-webhook')
router.register(r'analytics', SalesAnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]

