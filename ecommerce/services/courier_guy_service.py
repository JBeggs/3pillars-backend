"""
The Courier Guy service for shipping and Pudo integration.
Handles Courier Guy API integration for shipping and pickup point management.
"""
import logging
import requests
from typing import Optional, Dict, Any, List
from django.conf import settings

from ..models import EcommerceCompany, CompanyIntegrationSettings, Order

logger = logging.getLogger(__name__)


class CourierGuyService:
    """
    Service for The Courier Guy API integration.
    Each company has their own Courier Guy credentials.
    """
    
    # Courier Guy API endpoints
    SANDBOX_BASE_URL = 'https://api.thecourierguy.co.za/api'
    PRODUCTION_BASE_URL = 'https://api.thecourierguy.co.za/api'
    
    def __init__(self, company: EcommerceCompany):
        """
        Initialize Courier Guy service for a company.
        
        Uses company-specific settings if available, otherwise falls back to global settings.
        
        Args:
            company: EcommerceCompany instance
        """
        self.company = company
        self.integration_settings = self._get_integration_settings()
        self.credentials = self.integration_settings.get_courier_guy_credentials()
        self.base_url = self.SANDBOX_BASE_URL if self.credentials.get('sandbox_mode', True) else self.PRODUCTION_BASE_URL
    
    def _get_integration_settings(self) -> CompanyIntegrationSettings:
        """Get or create integration settings for company (will fallback to global if not set)."""
        settings, _ = CompanyIntegrationSettings.objects.get_or_create(
            company=self.company
        )
        return settings
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Courier Guy API requests."""
        api_key = self.credentials.get('api_key')
        api_secret = self.credentials.get('api_secret')
        
        if not api_key or not api_secret:
            raise ValueError(
                f"Courier Guy credentials not configured for company {self.company.name}. "
                f"Please configure company-specific credentials or set up global Courier Guy settings."
            )
        
        # Courier Guy typically uses API key authentication
        # Adjust based on actual API documentation
        return {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'X-API-Key': api_key,
            'X-API-Secret': api_secret,
        }
    
    def search_pudo_locations(
        self,
        postal_code: Optional[str] = None,
        city: Optional[str] = None,
        province: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: float = 10.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for Pudo pickup points.
        
        Args:
            postal_code: Postal code to search near
            city: City name
            province: Province name
            latitude: Latitude for location-based search
            longitude: Longitude for location-based search
            radius: Search radius in km
            limit: Maximum number of results
        
        Returns:
            List of Pudo location dictionaries
        """
        # TODO: Implement actual Courier Guy API call
        # This is a placeholder - adjust based on actual API documentation
        
        params = {}
        if postal_code:
            params['postal_code'] = postal_code
        if city:
            params['city'] = city
        if province:
            params['province'] = province
        if latitude and longitude:
            params['latitude'] = latitude
            params['longitude'] = longitude
            params['radius'] = radius
        
        params['limit'] = limit
        
        try:
            # Example API call - adjust endpoint and parameters based on actual API
            response = requests.get(
                f'{self.base_url}/pudo/locations',
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            # Transform response to match expected format
            return self._transform_pudo_locations(data.get('locations', []))
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Courier Guy API error searching Pudo locations: {e}")
            # Return empty list on error (or raise based on requirements)
            return []
    
    def _transform_pudo_locations(self, locations: List[Dict]) -> List[Dict[str, Any]]:
        """Transform Courier Guy API response to standard format."""
        transformed = []
        for loc in locations:
            transformed.append({
                'id': loc.get('id', ''),
                'name': loc.get('name', ''),
                'address': loc.get('address', ''),
                'city': loc.get('city', ''),
                'postalCode': loc.get('postal_code', ''),
                'province': loc.get('province', ''),
                'country': 'ZA',
                'latitude': loc.get('latitude'),
                'longitude': loc.get('longitude'),
                'operatingHours': loc.get('operating_hours', {}),
                'contact': {
                    'phone': loc.get('phone', ''),
                    'email': loc.get('email', '')
                },
                'features': loc.get('features', [])
            })
        return transformed
    
    def create_shipment(
        self,
        order: Order,
        pudo_pickup_point_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a shipment for an order.
        
        Args:
            order: Order instance
            pudo_pickup_point_id: Pudo pickup point ID (if Pudo delivery)
        
        Returns:
            Shipment information with waybill number, tracking, etc.
        """
        if not self.credentials.get('api_key'):
            raise ValueError(f"Courier Guy credentials not configured for company {self.company.name}")
        
        # Prepare shipment data
        shipment_data = {
            'account_number': self.credentials.get('account_number'),
            'order_number': order.order_number,
            'customer_name': f"{order.customer_first_name} {order.customer_last_name}",
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone or '',
            'delivery_address': order.shipping_address,
            'parcel_value': float(order.total),
            'parcel_weight': 0.5,  # Default or calculate from order items
            'delivery_method': order.delivery_method,
        }
        
        if pudo_pickup_point_id:
            shipment_data['pudo_pickup_point_id'] = pudo_pickup_point_id
        
        try:
            response = requests.post(
                f'{self.base_url}/shipments',
                json=shipment_data,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Update order with shipment info
            order.waybill_number = data.get('waybill_number')
            order.tracking_number = data.get('tracking_number')
            order.collection_code = data.get('collection_code')
            order.courier = {
                'name': 'courier_guy',
                'serviceCode': data.get('service_code', 'STANDARD'),
                'waybillNumber': data.get('waybill_number')
            }
            order.save()
            
            return {
                'shipmentId': data.get('shipment_id'),
                'waybillNumber': data.get('waybill_number'),
                'trackingNumber': data.get('tracking_number'),
                'collectionCode': data.get('collection_code'),
                'labelUrl': data.get('label_url'),
                'estimatedPickupDate': data.get('estimated_pickup_date')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Courier Guy API error creating shipment for order {order.order_number}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise ValueError(f"Failed to create Courier Guy shipment: {str(e)}")
    
    def track_shipment(self, waybill_number: str) -> Optional[Dict[str, Any]]:
        """
        Track a shipment by waybill number.
        
        Args:
            waybill_number: Courier Guy waybill number
        
        Returns:
            Tracking information or None if not found
        """
        try:
            response = requests.get(
                f'{self.base_url}/shipments/{waybill_number}/track',
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'waybillNumber': waybill_number,
                'status': data.get('status'),
                'statusDescription': data.get('status_description'),
                'currentLocation': data.get('current_location'),
                'events': data.get('events', []),
                'estimatedDelivery': data.get('estimated_delivery'),
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Courier Guy API error tracking shipment {waybill_number}: {e}")
            return None

