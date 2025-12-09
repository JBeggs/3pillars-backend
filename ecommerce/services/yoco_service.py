"""
Yoco payment gateway service.
Handles Yoco API integration for payment processing.
"""
import logging
import requests
import hmac
import hashlib
from typing import Optional, Dict, Any
from django.conf import settings

from ..models import EcommerceCompany, CompanyIntegrationSettings, Order

logger = logging.getLogger(__name__)


class YocoService:
    """
    Service for Yoco payment gateway integration.
    Each company has their own Yoco credentials.
    """
    
    # Yoco API endpoints
    SANDBOX_BASE_URL = 'https://online.yoco.com/v1'
    PRODUCTION_BASE_URL = 'https://online.yoco.com/v1'
    
    def __init__(self, company: EcommerceCompany):
        """
        Initialize Yoco service for a company.
        
        Uses company-specific settings if available, otherwise falls back to global settings.
        
        Args:
            company: EcommerceCompany instance
        """
        self.company = company
        self.integration_settings = self._get_integration_settings()
        self.credentials = self.integration_settings.get_yoco_credentials()
        self.base_url = self.SANDBOX_BASE_URL if self.credentials.get('sandbox_mode', True) else self.PRODUCTION_BASE_URL
    
    def _get_integration_settings(self) -> CompanyIntegrationSettings:
        """Get or create integration settings for company (will fallback to global if not set)."""
        settings, _ = CompanyIntegrationSettings.objects.get_or_create(
            company=self.company
        )
        return settings
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Yoco API requests."""
        secret_key = self.credentials.get('secret_key')
        if not secret_key:
            raise ValueError(
                f"Yoco secret key not configured for company {self.company.name}. "
                f"Please configure company-specific credentials or set up global Yoco settings."
            )
        
        return {
            'Authorization': f'Bearer {secret_key}',
            'Content-Type': 'application/json',
        }
    
    def create_checkout_session(
        self,
        order: Order,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Yoco checkout session for an order.
        
        Args:
            order: Order instance
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
            metadata: Additional metadata to attach to checkout
        
        Returns:
            Dict with checkoutId and redirectUrl
        """
        if not self.credentials.get('secret_key'):
            raise ValueError(
                f"Yoco secret key not configured for company {self.company.name}. "
                f"Please configure company-specific credentials or set up global Yoco settings."
            )
        
        # Convert amount to cents (Yoco uses cents)
        amount_cents = int(float(order.total) * 100)
        
        payload = {
            'amount': amount_cents,
            'currency': order.currency or 'ZAR',
            'successUrl': success_url,
            'cancelUrl': cancel_url,
            'metadata': {
                'order_id': str(order.id),
                'order_number': order.order_number,
                'company_id': str(self.company.id),
                **(metadata or {})
            }
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/checkouts',
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Store checkout ID in order
            order.yoco_checkout_id = data.get('id')
            order.save(update_fields=['yoco_checkout_id'])
            
            return {
                'checkoutId': data.get('id'),
                'redirectUrl': data.get('redirectUrl') or f"https://payments.yoco.com/checkout/{data.get('id')}",
                'orderId': str(order.id)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Yoco API error creating checkout for order {order.order_number}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise ValueError(f"Failed to create Yoco checkout: {str(e)}")
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Yoco webhook signature.
        
        Args:
            payload: Raw request body
            signature: Signature from X-Yoco-Signature header
            webhook_secret: Webhook secret from company settings
        
        Returns:
            True if signature is valid
        """
        webhook_secret = self.credentials.get('webhook_secret')
        if not webhook_secret:
            logger.warning(f"Yoco webhook secret not configured for company {self.company.name}")
            return False
        
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def get_payment_status(self, checkout_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payment status for a checkout session.
        
        Args:
            checkout_id: Yoco checkout ID
        
        Returns:
            Payment status information or None if not found
        """
        try:
            response = requests.get(
                f'{self.base_url}/checkouts/{checkout_id}',
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Yoco API error getting payment status for checkout {checkout_id}: {e}")
            return None

