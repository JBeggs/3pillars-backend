"""
Order management viewsets.
Multi-tenant order management with company isolation.
"""
import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg

from .models import Order, OrderItem, Cart, CartItem, EcommerceProduct
from .serializers import (
    OrderSerializer, OrderItemSerializer,
    CreateOrderSerializer, UpdateOrderStatusSerializer,
    UpdatePaymentSerializer, UpdateTrackingSerializer,
    CancelOrderSerializer
)
from .permissions import IsCompanyMember
from .utils import get_company_from_request

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order management (company-scoped).
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'delivery_method']
    search_fields = ['order_number', 'customer_email', 'customer_first_name', 'customer_last_name']
    ordering_fields = ['created_at', 'total', 'order_number']
    ordering = ['-created_at']
    lookup_field = 'id'
    
    def get_queryset(self):
        """Filter orders by company."""
        company = get_company_from_request(self.request)
        queryset = Order.objects.all()
        
        if company:
            queryset = queryset.filter(company=company)
        
        # Additional filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        customer_id = self.request.query_params.get('customerId')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        start_date = self.request.query_params.get('startDate')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        end_date = self.request.query_params.get('endDate')
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.select_related('company', 'customer').prefetch_related('items')
    
    @action(detail=False, methods=['post'], url_path='create-from-cart')
    def create_from_cart(self, request):
        """Create order from cart."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreateOrderSerializer(data=request.data)
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
        
        if cart.items.count() == 0:
            return Response(
                {'success': False, 'error': {'code': 'CART_EMPTY', 'message': 'Cart is empty'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate all products still in stock
        for item in cart.items.all():
            product = item.product
            if not product.in_stock:
                return Response(
                    {'success': False, 'error': {'code': 'OUT_OF_STOCK', 'message': f'{product.name} is out of stock'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if product.track_inventory and product.stock_quantity:
                if item.quantity > product.stock_quantity:
                    return Response(
                        {'success': False, 'error': {'code': 'INSUFFICIENT_STOCK', 'message': f'Only {product.stock_quantity} {product.name} available'}},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Create order
        with transaction.atomic():
            customer_data = serializer.validated_data['customer']
            shipping_address = serializer.validated_data['shipping_address']
            delivery_method = serializer.validated_data['delivery_method']
            pudo_pickup_point = serializer.validated_data.get('pudo_pickup_point', {})
            notes = serializer.validated_data.get('notes', '')
            
            order = Order.objects.create(
                company=company,
                customer=user,
                session_id=session_id,
                status='pending',
                subtotal=cart.subtotal,
                shipping=cart.shipping,
                tax=cart.tax,
                discount=cart.discount,
                total=cart.total,
                payment_method='yoco',
                payment_status='pending',
                customer_first_name=customer_data.get('firstName', ''),
                customer_last_name=customer_data.get('lastName', ''),
                customer_email=customer_data.get('email', ''),
                customer_phone=customer_data.get('phone', ''),
                shipping_address=shipping_address,
                delivery_method=delivery_method,
                pudo_pickup_point=pudo_pickup_point,
                currency=cart.currency,
                notes=notes,
            )
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product_name,
                    product_image=cart_item.product_image,
                    product_sku=cart_item.product_sku,
                    price=cart_item.price,
                    quantity=cart_item.quantity,
                )
                
                # Update inventory if tracking
                if cart_item.product.track_inventory and cart_item.product.stock_quantity:
                    cart_item.product.stock_quantity -= cart_item.quantity
                    if cart_item.product.stock_quantity <= 0:
                        cart_item.product.in_stock = False
                    cart_item.product.save()
            
            # Clear cart
            cart.items.all().delete()
            cart.calculate_totals()
            cart.save()
        
        serializer = self.get_serializer(order)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='number/(?P<order_number>[^/.]+)')
    def get_by_order_number(self, request, order_number=None):
        """Get order by order number."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(company=company, order_number=order_number)
            serializer = self.get_serializer(order)
            return Response({'success': True, 'data': serializer.data})
        except Order.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'ORDER_NOT_FOUND', 'message': f'Order {order_number} not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['put'], url_path='status')
    def update_status(self, request, id=None):
        """Update order status."""
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        
        # Update status and timestamps
        order.status = new_status
        if notes:
            order.notes = (order.notes or '') + f'\n{notes}'
        
        if new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
        elif new_status == 'cancelled' and not order.cancelled_at:
            order.cancelled_at = timezone.now()
        
        order.save()
        
        serializer = self.get_serializer(order)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=True, methods=['put'], url_path='payment')
    def update_payment(self, request, id=None):
        """Update payment information (typically from Yoco webhook)."""
        order = self.get_object()
        serializer = UpdatePaymentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_data = serializer.validated_data['payment']
        new_status = serializer.validated_data['status']
        
        # Update payment info
        order.payment_status = payment_data.get('status', order.payment_status)
        order.yoco_payment_id = payment_data.get('yocoPaymentId', order.yoco_payment_id)
        order.transaction_id = payment_data.get('transactionId', order.transaction_id)
        
        if payment_data.get('paidAt'):
            from datetime import datetime
            order.paid_at = datetime.fromisoformat(str(payment_data['paidAt']).replace('Z', '+00:00'))
        elif order.payment_status == 'completed' and not order.paid_at:
            order.paid_at = timezone.now()
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=True, methods=['put'], url_path='tracking')
    def update_tracking(self, request, id=None):
        """Add shipping tracking information."""
        order = self.get_object()
        serializer = UpdateTrackingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.tracking_number = serializer.validated_data.get('trackingNumber', order.tracking_number)
        order.waybill_number = serializer.validated_data.get('waybillNumber', order.waybill_number)
        order.collection_code = serializer.validated_data.get('collectionCode', order.collection_code)
        
        if serializer.validated_data.get('status'):
            order.status = serializer.validated_data['status']
        
        if serializer.validated_data.get('shippedAt'):
            order.shipped_at = timezone.datetime.fromisoformat(serializer.validated_data['shippedAt'].replace('Z', '+00:00'))
        elif order.status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
        
        if serializer.validated_data.get('estimatedDelivery'):
            order.estimated_delivery = timezone.datetime.fromisoformat(serializer.validated_data['estimatedDelivery'].replace('Z', '+00:00'))
        
        if serializer.validated_data.get('courier'):
            order.courier = serializer.validated_data['courier']
        
        if serializer.validated_data.get('pudoPickupPoint'):
            order.pudo_pickup_point = serializer.validated_data['pudoPickupPoint']
        
        order.save()
        
        serializer = self.get_serializer(order)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=True, methods=['put'], url_path='cancel')
    def cancel_order(self, request, id=None):
        """Cancel an order."""
        order = self.get_object()
        
        if order.status not in ['pending', 'paid']:
            return Response(
                {'success': False, 'error': {'code': 'ORDER_CANNOT_BE_CANCELLED', 'message': 'Order cannot be cancelled in current status'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CancelOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = serializer.validated_data['reason']
        refund = serializer.validated_data.get('refund', False)
        
        # Update order
        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        if reason:
            order.notes = (order.notes or '') + f'\nCancelled: {reason}'
        order.save()
        
        # TODO: Process refund if requested
        if refund and order.payment_status == 'completed':
            # Implement refund logic
            pass
        
        # Restore inventory
        for item in order.items.all():
            if item.product.track_inventory and item.product.stock_quantity is not None:
                item.product.stock_quantity += item.quantity
                item.product.in_stock = True
                item.product.save()
        
        serializer = self.get_serializer(order)
        return Response({'success': True, 'data': serializer.data})
    
    def list(self, request, *args, **kwargs):
        """Override list to return paginated response with success wrapper."""
        response = super().list(request, *args, **kwargs)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('limit', 20))
        count = response.data.get('count', 0)
        return Response({
            'success': True,
            'data': response.data.get('results', []),
            'pagination': {
                'page': page,
                'limit': page_size,
                'total': count,
                'totalPages': (count + page_size - 1) // page_size if page_size > 0 else 0,
                'hasNext': response.data.get('next') is not None,
                'hasPrev': response.data.get('previous') is not None,
            }
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return success wrapper."""
        response = super().retrieve(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})
    
    def create(self, request, *args, **kwargs):
        """Override create - use create_from_cart instead."""
        return Response(
            {'success': False, 'error': {'code': 'USE_CREATE_FROM_CART', 'message': 'Use POST /orders/create-from-cart/ to create orders from cart'}},
            status=status.HTTP_400_BAD_REQUEST
        )

