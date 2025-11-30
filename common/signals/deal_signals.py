"""
Signals for Deal model to handle company activation.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from crm.models import Deal

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Deal)
def handle_deal_completion(sender, instance, created, **kwargs):
    """
    When a deal is marked as won/completed, activate the associated company.
    This is for registration deals - when the deal is completed, the company can use the site.
    """
    # Only process if deal is not new and has a win_closing_date (deal is won)
    if created or not instance.win_closing_date:
        return
    
    # Check if this is a registration deal
    from ecommerce.models import EcommerceCompany
    try:
        company = EcommerceCompany.objects.get(registration_deal=instance)
    except EcommerceCompany.DoesNotExist:
        # Not a registration deal, ignore
        return
    
    # Only activate if currently trial (pending approval)
    if company.status != 'trial':
        return
    
    # Activate the company
    company.status = 'active'
    company.save(update_fields=['status'])
    
    logger.info(f"Company {company.name} activated after deal {instance.id} completion")
    
    # Send FCM notification to company owner
    from fcm.services import fcm_service
    from ecommerce.utils import get_user_company
    
    # Get company for FCM context (use the company itself)
    try:
        fcm_service.send_to_user(
            user=company.owner,
            title='Account Activated',
            body=f'Your {company.product.name if company.product else "account"} has been approved. You can now manage your products.',
            data={
                'type': 'company_activated',
                'company_id': str(company.id),
            },
            notification_type='deal_won_lost',
            company=company
        )
    except Exception as e:
        logger.error(f"Failed to send activation notification: {e}")

