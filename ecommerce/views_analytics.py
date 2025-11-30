"""
Sales analytics viewsets.
Multi-tenant sales reporting and analytics.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta

from .models import Order, OrderItem, EcommerceProduct
from .permissions import IsCompanyMember
from .utils import get_company_from_request

logger = logging.getLogger(__name__)


class SalesAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for sales analytics (company-scoped).
    """
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    @action(detail=False, methods=['get'], url_path='sales/summary')
    def get_summary(self, request):
        """Get sales summary for the authenticated company."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get date range
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        group_by = request.query_params.get('groupBy', 'day')  # day, week, month
        
        # Build query
        orders = Order.objects.filter(company=company)
        
        if start_date:
            orders = orders.filter(created_at__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__lte=end_date)
        
        # Calculate summary
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        average_order_value = orders.aggregate(avg=Avg('total'))['avg'] or 0
        
        # Count items sold
        total_items_sold = OrderItem.objects.filter(
            order__company=company,
            order__in=orders
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Count by status
        by_status = {}
        for status_code, status_name in Order.STATUS_CHOICES:
            by_status[status_code] = orders.filter(status=status_code).count()
        
        # Group by day/week/month
        by_period = []
        if group_by == 'day':
            # Group by day
            from django.db.models.functions import TruncDate
            daily = orders.annotate(date=TruncDate('created_at')).values('date').annotate(
                orders=Count('id'),
                revenue=Sum('total')
            ).order_by('date')
            
            for item in daily:
                by_period.append({
                    'date': item['date'].isoformat() if item['date'] else None,
                    'orders': item['orders'],
                    'revenue': float(item['revenue'] or 0)
                })
        
        return Response({
            'success': True,
            'data': {
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'summary': {
                    'totalOrders': total_orders,
                    'totalRevenue': float(total_revenue),
                    'averageOrderValue': float(average_order_value),
                    'totalItemsSold': total_items_sold,
                    'pendingOrders': by_status.get('pending', 0),
                    'paidOrders': by_status.get('paid', 0),
                    'cancelledOrders': by_status.get('cancelled', 0)
                },
                'byStatus': by_status,
                'byDay': by_period if group_by == 'day' else []
            }
        })
    
    @action(detail=False, methods=['get'], url_path='sales/products')
    def get_top_products(self, request):
        """Get top-selling products."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        limit = int(request.query_params.get('limit', 10))
        
        # Build query
        orders = Order.objects.filter(company=company, status__in=['paid', 'processing', 'shipped', 'delivered'])
        
        if start_date:
            orders = orders.filter(created_at__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__lte=end_date)
        
        # Get top products
        top_products = OrderItem.objects.filter(
            order__in=orders
        ).values(
            'product_id', 'product_name'
        ).annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum('subtotal'),
            orders=Count('order_id', distinct=True)
        ).order_by('-quantity_sold')[:limit]
        
        data = []
        for item in top_products:
            data.append({
                'productId': str(item['product_id']),
                'productName': item['product_name'],
                'quantitySold': item['quantity_sold'],
                'revenue': float(item['revenue'] or 0),
                'orders': item['orders']
            })
        
        return Response({'success': True, 'data': data})
    
    @action(detail=False, methods=['get'], url_path='sales/trends')
    def get_trends(self, request):
        """Get revenue trends over time."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        group_by = request.query_params.get('groupBy', 'day')  # day, week, month
        
        # Build query
        orders = Order.objects.filter(company=company, status__in=['paid', 'processing', 'shipped', 'delivered'])
        
        if start_date:
            orders = orders.filter(created_at__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__lte=end_date)
        
        # Group by period
        from django.db.models.functions import TruncDate
        trends_data = orders.annotate(date=TruncDate('created_at')).values('date').annotate(
            revenue=Sum('total'),
            orders=Count('id'),
            averageOrderValue=Avg('total')
        ).order_by('date')
        
        trends = []
        for item in trends_data:
            trends.append({
                'date': item['date'].isoformat() if item['date'] else None,
                'revenue': float(item['revenue'] or 0),
                'orders': item['orders'],
                'averageOrderValue': float(item['averageOrderValue'] or 0)
            })
        
        # Calculate growth (compare first half vs second half)
        if len(trends) > 1:
            mid_point = len(trends) // 2
            first_half_revenue = sum(t['revenue'] for t in trends[:mid_point])
            second_half_revenue = sum(t['revenue'] for t in trends[mid_point:])
            
            if first_half_revenue > 0:
                revenue_growth = ((second_half_revenue - first_half_revenue) / first_half_revenue) * 100
            else:
                revenue_growth = 0
            
            first_half_orders = sum(t['orders'] for t in trends[:mid_point])
            second_half_orders = sum(t['orders'] for t in trends[mid_point:])
            
            if first_half_orders > 0:
                orders_growth = ((second_half_orders - first_half_orders) / first_half_orders) * 100
            else:
                orders_growth = 0
        else:
            revenue_growth = 0
            orders_growth = 0
        
        return Response({
            'success': True,
            'data': {
                'period': group_by,
                'trends': trends,
                'growth': {
                    'revenue': round(revenue_growth, 2),
                    'orders': round(orders_growth, 2)
                }
            }
        })

