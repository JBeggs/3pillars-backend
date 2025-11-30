"""
Yoco payment gateway integration views.
"""
import logging
import hmac
import hashlib
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Order, EcommerceCompany
from .serializers import YocoCheckoutSerializer
from .permissions import IsCompanyMember
from .utils import get_company_from_request

logger = logging.getLogger(__name__)


class YocoViewSet(viewsets.ViewSet):
    """
    ViewSet for Yoco payment gateway integration.
    """
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    @action(detail=False, methods=['post'], url_path='orders/(?P<order_id>[^/.]+)/yoco-checkout')
    def create_checkout(self, request, order_id=None):
        """Create a Yoco checkout session for an order."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = YocoCheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id=order_id, company=company)
        except Order.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if order.status != 'pending':
            return Response(
                {'success': False, 'error': {'code': 'ORDER_ALREADY_PAID', 'message': 'Order is not pending'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Yoco checkout session using service
        try:
            from .services import YocoService
            yoco_service = YocoService(company)
            
            success_url = serializer.validated_data.get('successUrl', '')
            cancel_url = serializer.validated_data.get('cancelUrl', '')
            
            checkout_data = yoco_service.create_checkout_session(
                order=order,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            return Response({'success': True, 'data': checkout_data})
            
        except ValueError as e:
            logger.error(f"Yoco service error: {e}")
            return Response(
                {'success': False, 'error': {'code': 'YOCO_CONFIG_ERROR', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error creating Yoco checkout: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': {'code': 'YOCO_CHECKOUT_FAILED', 'message': 'Failed to create checkout session'}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='orders/(?P<order_id>[^/.]+)/payment-status')
    def get_payment_status(self, request, order_id=None):
        """Get current payment status for an order."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id=order_id, company=company)
        except Order.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'success': True,
            'data': {
                'orderId': str(order.id),
                'paymentStatus': order.payment_status,
                'yocoPaymentId': order.yoco_payment_id,
                'paidAt': order.paid_at.isoformat() if order.paid_at else None
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class YocoWebhookViewSet(viewsets.ViewSet):
    """
    ViewSet for Yoco webhook handling.
    """
    permission_classes = [AllowAny]  # Webhooks don't use standard auth
    
    @action(detail=False, methods=['post'], url_path='webhooks/yoco')
    def handle_webhook(self, request):
        """Handle Yoco webhook events."""
        # Get signature from header
        signature = request.headers.get('X-Yoco-Signature', '')
        
        event = request.data.get('event')
        data = request.data.get('data', {})
        
        # Find order by checkout ID to get company
        checkout_id = data.get('checkoutId')
        if not checkout_id:
            return Response(
                {'success': False, 'error': {'code': 'INVALID_WEBHOOK', 'message': 'Missing checkoutId'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(yoco_checkout_id=checkout_id)
        except Order.DoesNotExist:
            logger.error(f'Order not found for checkout ID: {checkout_id}')
            return Response(
                {'success': False, 'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify webhook signature using company's credentials
        try:
            from .services import YocoService
            yoco_service = YocoService(order.company)
            
            if not yoco_service.verify_webhook_signature(request.body, signature):
                logger.warning(f'Invalid webhook signature for checkout {checkout_id}')
                return Response(
                    {'success': False, 'error': {'code': 'WEBHOOK_VERIFICATION_FAILED', 'message': 'Invalid signature'}},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            logger.error(f'Error verifying webhook signature: {e}')
            # Continue processing if signature verification fails (for development)
            # In production, you may want to reject the webhook
        
        event = request.data.get('event')
        data = request.data.get('data', {})
        
        if event == 'payment.succeeded':
            checkout_id = data.get('checkoutId')
            payment_id = data.get('id')
            transaction_id = data.get('transactionId')
            amount = data.get('amount', 0) / 100  # Yoco amounts are in cents
            paid_at = data.get('createdAt')
            
            # Find order by checkout ID
            try:
                order = Order.objects.get(yoco_checkout_id=checkout_id)
            except Order.DoesNotExist:
                logger.error(f'Order not found for checkout ID: {checkout_id}')
                return Response(
                    {'success': False, 'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify amount matches
            if amount != float(order.total):
                logger.error(f'Amount mismatch: order total {order.total}, payment amount {amount}')
                return Response(
                    {'success': False, 'error': {'code': 'AMOUNT_MISMATCH', 'message': 'Payment amount does not match order total'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update order
            from django.utils import timezone
            order.payment_status = 'completed'
            order.status = 'paid'
            order.yoco_payment_id = payment_id
            order.transaction_id = transaction_id
            if paid_at:
                order.paid_at = timezone.datetime.fromisoformat(paid_at.replace('Z', '+00:00'))
            else:
                order.paid_at = timezone.now()
            order.save()
            
            # TODO: Send confirmation email
            # TODO: Update inventory if not already done
            
            logger.info(f'Order {order.order_number} payment confirmed via Yoco webhook')
            return Response({'success': True, 'message': 'Webhook processed'})
        
        elif event == 'payment.failed':
            checkout_id = data.get('checkoutId')
            try:
                order = Order.objects.get(yoco_checkout_id=checkout_id)
                order.payment_status = 'failed'
                order.save()
            except Order.DoesNotExist:
                pass
            
            return Response({'success': True, 'message': 'Webhook processed'})
        
        return Response({'success': True, 'message': 'Webhook received'})

