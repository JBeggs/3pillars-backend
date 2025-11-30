"""
Pudo pickup point integration views.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Order
from .serializers import PudoLocationSerializer, PudoShipmentSerializer
from .permissions import IsCompanyMember
from .utils import get_company_from_request

logger = logging.getLogger(__name__)


class PudoViewSet(viewsets.ViewSet):
    """
    ViewSet for Pudo pickup point integration.
    """
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    @action(detail=False, methods=['get'], url_path='locations')
    def search_locations(self, request):
        """
        Search for Pudo pickup points.
        TODO: Integrate with actual Pudo API or The Courier Guy API.
        """
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        postal_code = request.query_params.get('postalCode')
        city = request.query_params.get('city')
        province = request.query_params.get('province')
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = float(request.query_params.get('radius', 10))
        limit = int(request.query_params.get('limit', 20))
        
        # Call Courier Guy API for Pudo locations
        try:
            from .services import CourierGuyService
            courier_service = CourierGuyService(company)
            
            locations = courier_service.search_pudo_locations(
                postal_code=postal_code,
                city=city,
                province=province,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                radius=radius,
                limit=limit
            )
            
            serializer = PudoLocationSerializer(locations, many=True)
            return Response({'success': True, 'data': serializer.data})
            
        except ValueError as e:
            logger.error(f"Courier Guy service error: {e}")
            # Fall back to mock data if credentials not configured
            logger.warning("Falling back to mock Pudo locations")
        except Exception as e:
            logger.error(f"Error searching Pudo locations: {e}", exc_info=True)
            # Fall back to mock data on error
        
        # Fallback: Return mock data
        mock_locations = [
            {
                'id': 'pudo-12345',
                'name': 'Pudo Pickup Point - Pick n Pay Centurion',
                'address': 'Shop 45, Centurion Mall, Cnr Heuwel & Lenchen Road',
                'city': 'Centurion',
                'postalCode': '0157',
                'province': 'Gauteng',
                'country': 'ZA',
                'latitude': -25.8603,
                'longitude': 28.1892,
                'distance': 2.5 if latitude and longitude else None,
                'operatingHours': {
                    'monday': '08:00-18:00',
                    'tuesday': '08:00-18:00',
                    'wednesday': '08:00-18:00',
                    'thursday': '08:00-18:00',
                    'friday': '08:00-18:00',
                    'saturday': '08:00-17:00',
                    'sunday': '09:00-14:00',
                },
                'contact': {
                    'phone': '+27 12 345 6789'
                },
                'features': ['parking', 'wheelchair-accessible', 'atm']
            }
        ]
        
        # Filter by location if provided
        if postal_code:
            mock_locations = [loc for loc in mock_locations if loc['postalCode'] == postal_code]
        if city:
            mock_locations = [loc for loc in mock_locations if city.lower() in loc['city'].lower()]
        if province:
            mock_locations = [loc for loc in mock_locations if province.lower() in loc['province'].lower()]
        
        # Limit results
        mock_locations = mock_locations[:limit]
        
        serializer = PudoLocationSerializer(mock_locations, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['get'], url_path='locations/(?P<location_id>[^/.]+)')
    def get_location(self, request, location_id=None):
        """Get detailed information about a specific Pudo location."""
        # TODO: Call actual Pudo API
        mock_location = {
            'id': location_id,
            'name': 'Pudo Pickup Point - Pick n Pay Centurion',
            'address': 'Shop 45, Centurion Mall, Cnr Heuwel & Lenchen Road',
            'city': 'Centurion',
            'postalCode': '0157',
            'province': 'Gauteng',
            'country': 'ZA',
            'latitude': -25.8603,
            'longitude': 28.1892,
            'operatingHours': {
                'monday': '08:00-18:00',
                'tuesday': '08:00-18:00',
                'wednesday': '08:00-18:00',
                'thursday': '08:00-18:00',
                'friday': '08:00-18:00',
                'saturday': '08:00-17:00',
                'sunday': '09:00-14:00',
            },
            'contact': {
                'phone': '+27 12 345 6789',
                'email': 'centurion@pudo.co.za'
            },
            'features': ['parking', 'wheelchair-accessible', 'atm']
        }
        
        serializer = PudoLocationSerializer(mock_location)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['get'], url_path='shipments/(?P<waybill_number>[^/.]+)/track')
    def track_shipment(self, request, waybill_number=None):
        """Track a Pudo shipment by waybill number."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find order with this waybill number
        try:
            order = Order.objects.get(company=company, waybill_number=waybill_number)
        except Order.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'SHIPMENT_NOT_FOUND', 'message': 'Shipment not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # TODO: Call actual Pudo API to get tracking status
        # For now, return mock data based on order status
        status_map = {
            'shipped': 'in_transit',
            'delivered': 'delivered',
        }
        
        mock_tracking = {
            'waybillNumber': waybill_number,
            'status': status_map.get(order.status, 'pending'),
            'statusDescription': f'Order is {order.status}',
            'currentLocation': 'Johannesburg Distribution Centre',
            'events': [
                {
                    'timestamp': order.shipped_at.isoformat() if order.shipped_at else order.created_at.isoformat(),
                    'status': 'collected',
                    'description': 'Parcel collected from sender'
                }
            ],
            'estimatedDelivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            'pudoPickupPoint': order.pudo_pickup_point if order.pudo_pickup_point else None
        }
        
        return Response({'success': True, 'data': mock_tracking})


class PudoShipmentViewSet(viewsets.ViewSet):
    """
    ViewSet for creating Pudo shipments.
    """
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    @action(detail=False, methods=['post'], url_path='orders/(?P<order_id>[^/.]+)/pudo-shipment')
    def create_shipment(self, request, order_id=None):
        """Create a Pudo shipment for an order."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PudoShipmentSerializer(data=request.data)
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
        
        if order.status != 'paid':
            return Response(
                {'success': False, 'error': {'code': 'ORDER_NOT_PAID', 'message': 'Order must be paid before creating shipment'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create shipment using Courier Guy service
        try:
            from .services import CourierGuyService
            courier_service = CourierGuyService(company)
            
            pudo_pickup_point_id = serializer.validated_data.get('pudoPickupPointId')
            
            shipment_data = courier_service.create_shipment(
                order=order,
                pudo_pickup_point_id=pudo_pickup_point_id
            )
            
            # Update order status
            from django.utils import timezone
            order.status = 'shipped'
            order.shipped_at = timezone.now()
            order.save()
            
            # Get Pudo pickup point from order
            pudo_pickup_point = order.pudo_pickup_point or {}
            
            shipment_data['pudoPickupPoint'] = {
                'id': pudo_pickup_point.get('id', ''),
                'name': pudo_pickup_point.get('name', ''),
                'address': pudo_pickup_point.get('address', ''),
            }
            
            return Response({'success': True, 'data': shipment_data})
            
        except ValueError as e:
            logger.error(f"Courier Guy service error: {e}")
            return Response(
                {'success': False, 'error': {'code': 'COURIER_CONFIG_ERROR', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error creating shipment: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': {'code': 'SHIPMENT_CREATION_FAILED', 'message': 'Failed to create shipment'}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

