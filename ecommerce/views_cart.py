"""
Cart management viewsets.
Multi-tenant cart management with company isolation.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Cart, CartItem, EcommerceProduct, EcommerceCompany
from .serializers import (
    CartSerializer, CartItemSerializer,
    AddCartItemSerializer, UpdateCartItemSerializer,
    UpdateShippingSerializer, ApplyDiscountSerializer
)
from .permissions import IsCompanyMember
from .utils import get_company_from_request

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cart management (company-scoped).
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    def get_queryset(self):
        """Filter carts by company."""
        company = get_company_from_request(self.request)
        queryset = Cart.objects.all()
        
        if company:
            queryset = queryset.filter(company=company)
        
        # Filter by user or session
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(user=user)
        else:
            session_id = self.request.session.session_key
            if session_id:
                queryset = queryset.filter(session_id=session_id)
        
        return queryset.select_related('company', 'user').prefetch_related('items__product')
    
    @action(detail=False, methods=['get'], url_path='me')
    def get_my_cart(self, request):
        """Get current user's cart (or create new if doesn't exist)."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create cart
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if not user else None
        
        cart, created = Cart.objects.get_or_create(
            company=company,
            defaults={
                'user': user,
                'session_id': session_id,
            }
        )
        
        # If cart exists but user/session changed, update it
        if not created:
            if user and not cart.user:
                cart.user = user
                cart.session_id = None
                cart.save()
            elif not user and session_id and not cart.session_id:
                cart.session_id = session_id
                cart.save()
        
        # Recalculate totals
        cart.calculate_totals()
        cart.save()
        
        serializer = self.get_serializer(cart)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        """Add item to cart."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AddCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            # Verify product belongs to company
            product = EcommerceProduct.objects.get(id=product_id, company=company)
        except EcommerceProduct.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock
        if not product.in_stock:
            return Response(
                {'success': False, 'error': {'code': 'OUT_OF_STOCK', 'message': 'Product is out of stock'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if product.track_inventory and product.stock_quantity:
            if quantity > product.stock_quantity:
                return Response(
                    {'success': False, 'error': {'code': 'INSUFFICIENT_STOCK', 'message': f'Only {product.stock_quantity} items available'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get or create cart
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if not user else None
        
        cart, _ = Cart.objects.get_or_create(
            company=company,
            defaults={
                'user': user,
                'session_id': session_id,
            }
        )
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'product_name': product.name,
                'product_image': product.image,
                'product_sku': product.sku,
                'price': product.price,
                'quantity': quantity,
            }
        )
        
        if not created:
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            if product.track_inventory and product.stock_quantity:
                if new_quantity > product.stock_quantity:
                    return Response(
                        {'success': False, 'error': {'code': 'INSUFFICIENT_STOCK', 'message': f'Only {product.stock_quantity} items available'}},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            cart_item.quantity = new_quantity
            cart_item.save()
        
        # Recalculate cart totals
        cart.calculate_totals()
        cart.save()
        
        serializer = self.get_serializer(cart)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['put'], url_path='items/(?P<product_id>[^/.]+)')
    def update_item(self, request, product_id=None):
        """Update cart item quantity."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quantity = serializer.validated_data['quantity']
        
        # Get cart
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if not user else None
        
        try:
            if user:
                cart = Cart.objects.get(company=company, user=user)
            else:
                cart = Cart.objects.get(company=company, session_id=session_id)
        except Cart.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'CART_NOT_FOUND', 'message': 'Cart not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get cart item
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'CART_ITEM_NOT_FOUND', 'message': 'Item not found in cart'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock
        product = cart_item.product
        if product.track_inventory and product.stock_quantity:
            if quantity > product.stock_quantity:
                return Response(
                    {'success': False, 'error': {'code': 'INSUFFICIENT_STOCK', 'message': f'Only {product.stock_quantity} items available'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        # Recalculate cart totals
        cart.calculate_totals()
        cart.save()
        
        serializer = self.get_serializer(cart)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<product_id>[^/.]+)')
    def remove_item(self, request, product_id=None):
        """Remove item from cart."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cart
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if not user else None
        
        try:
            if user:
                cart = Cart.objects.get(company=company, user=user)
            else:
                cart = Cart.objects.get(company=company, session_id=session_id)
        except Cart.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'CART_NOT_FOUND', 'message': 'Cart not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove item
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        
        # Recalculate cart totals
        cart.calculate_totals()
        cart.save()
        
        serializer = self.get_serializer(cart)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['delete'], url_path='me')
    def clear_cart(self, request):
        """Clear all items from cart."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cart
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if not user else None
        
        try:
            if user:
                cart = Cart.objects.get(company=company, user=user)
            else:
                cart = Cart.objects.get(company=company, session_id=session_id)
        except Cart.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'CART_NOT_FOUND', 'message': 'Cart not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Clear items
        cart.items.all().delete()
        cart.calculate_totals()
        cart.save()
        
        return Response({'success': True, 'message': 'Cart cleared successfully'})
    
    @action(detail=False, methods=['put'], url_path='me/shipping')
    def update_shipping(self, request):
        """Update shipping information in cart."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UpdateShippingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cart
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if not user else None
        
        try:
            if user:
                cart = Cart.objects.get(company=company, user=user)
            else:
                cart = Cart.objects.get(company=company, session_id=session_id)
        except Cart.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'CART_NOT_FOUND', 'message': 'Cart not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update shipping info
        if 'shipping_address' in serializer.validated_data:
            cart.shipping_address = serializer.validated_data['shipping_address']
        if 'delivery_method' in serializer.validated_data:
            cart.delivery_method = serializer.validated_data['delivery_method']
        if 'pudo_pickup_point' in serializer.validated_data:
            cart.pudo_pickup_point = serializer.validated_data['pudo_pickup_point']
        
        # Recalculate totals (shipping may change)
        cart.calculate_totals()
        cart.save()
        
        serializer = self.get_serializer(cart)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['post'], url_path='me/discount')
    def apply_discount(self, request):
        """Apply discount code to cart."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApplyDiscountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        code = serializer.validated_data['code']
        
        # Get cart
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if not user else None
        
        try:
            if user:
                cart = Cart.objects.get(company=company, user=user)
            else:
                cart = Cart.objects.get(company=company, session_id=session_id)
        except Cart.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'CART_NOT_FOUND', 'message': 'Cart not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # TODO: Validate discount code (implement discount code system)
        # For now, just store the code
        cart.discount_code = code
        cart.discount = 10.00  # Placeholder - implement actual discount calculation
        cart.calculate_totals()
        cart.save()
        
        serializer = self.get_serializer(cart)
        return Response({
            'success': True,
            'data': {
                'discount': float(cart.discount),
                'discountCode': cart.discount_code,
                **serializer.data
            }
        })

