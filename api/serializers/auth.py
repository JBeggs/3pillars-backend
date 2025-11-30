"""
Authentication serializers.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer for auth responses."""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_superuser', 'is_staff', 'is_active'
        ]
        read_only_fields = ['id', 'is_superuser', 'is_staff', 'is_active']


class TokenResponseSerializer(serializers.Serializer):
    """Token response serializer."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class RefreshTokenSerializer(serializers.Serializer):
    """Refresh token request serializer."""
    refresh = serializers.CharField()


class RefreshTokenResponseSerializer(serializers.Serializer):
    """Refresh token response serializer."""
    access = serializers.CharField()


class BusinessRegistrationSerializer(serializers.Serializer):
    """
    Serializer for business registration.
    Creates a user account and an EcommerceCompany.
    """
    # User fields
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    # Company fields
    company_name = serializers.CharField(max_length=200, required=True)
    company_email = serializers.EmailField(required=True)
    company_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    company_website = serializers.URLField(required=False, allow_blank=True)
    company_address_street = serializers.CharField(max_length=255, required=False, allow_blank=True)
    company_address_city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    company_address_province = serializers.CharField(max_length=100, required=False, allow_blank=True)
    company_address_postal_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    company_address_country = serializers.CharField(max_length=2, default='ZA', required=False)
    company_registration_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    company_tax_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    # Product selection (hidden, defaults to micro-sites)
    product_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate(self, attrs):
        """Validate registration data."""
        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists'})
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered'})
        
        # Check if company email already exists
        from ecommerce.models import EcommerceCompany
        if EcommerceCompany.objects.filter(email=attrs['company_email']).exists():
            raise serializers.ValidationError({'company_email': 'Company email already registered'})
        
        # Validate password match
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        
        # Get or default product (micro-sites)
        from common.models import Product
        product_id = attrs.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product_id': 'Invalid product selected'})
        else:
            # Default to micro-sites (or first default product)
            product = Product.objects.filter(is_default=True, is_active=True).first()
            if not product:
                product = Product.objects.filter(is_active=True).first()
            if not product:
                raise serializers.ValidationError({'product_id': 'No active products available'})
        
        attrs['product'] = product
        return attrs
    
    def create(self, validated_data):
        """Create user and company, then create deal and send notifications."""
        from ecommerce.models import EcommerceCompany
        from django.db import transaction
        from django.utils import timezone
        from datetime import timedelta
        
        product = validated_data.pop('product')
        
        with transaction.atomic():
            # Create user
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                is_active=True
            )
            
            # Generate company slug from name
            company_name = validated_data['company_name']
            base_slug = slugify(company_name)
            slug = base_slug
            counter = 1
            while EcommerceCompany.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Create company (status: trial until deal is completed, then activated to 'active')
            company = EcommerceCompany.objects.create(
                name=company_name,
                slug=slug,
                email=validated_data['company_email'],
                phone=validated_data.get('company_phone', ''),
                website=validated_data.get('company_website', ''),
                address_street=validated_data.get('company_address_street', ''),
                address_city=validated_data.get('company_address_city', ''),
                address_province=validated_data.get('company_address_province', ''),
                address_postal_code=validated_data.get('company_address_postal_code', ''),
                address_country=validated_data.get('company_address_country', 'ZA'),
                registration_number=validated_data.get('company_registration_number', ''),
                tax_number=validated_data.get('company_tax_number', ''),
                owner=user,
                product=product,
                status='trial',  # Start as trial, will be activated to 'active' when deal is completed
                plan='free'
            )
            
            # Create deal for this registration (with error handling)
            import logging
            logger = logging.getLogger(__name__)
            
            deal = None
            try:
                logger.info(f"Attempting to create registration deal for company {company.name}, product {product.name}")
                deal = self._create_registration_deal(user, company, product)
                if deal and deal.id:
                    company.registration_deal = deal
                    company.save(update_fields=['registration_deal'])
                    logger.info(f"✓ Successfully created and linked registration deal {deal.id} (ticket: {deal.ticket}) for company {company.name}")
                else:
                    logger.warning(f"⚠ Deal creation returned None or deal has no ID for company {company.name}")
            except Exception as e:
                logger.error(f"✗ Error creating registration deal for company {company.name}: {e}", exc_info=True)
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Continue even if deal creation fails - registration should still succeed
                deal = None
            
            # Create message for all staff (with error handling)
            if deal:
                try:
                    self._create_staff_message(user, company, product, deal)
                except Exception as e:
                    logger.error(f"Error creating staff message: {e}", exc_info=True)
            
            # Send FCM notification to all staff (with error handling)
            if deal:
                try:
                    self._notify_staff(user, company, product, deal)
                except Exception as e:
                    logger.error(f"Error sending FCM notifications: {e}", exc_info=True)
            
            return {
                'user': user,
                'company': company,
                'deal': deal
            }
    
    def _create_registration_deal(self, user, company, product):
        """Create a deal for the registration."""
        import logging
        logger = logging.getLogger(__name__)
        
        from crm.models import Deal, Stage
        from crm.utils.ticketproc import new_ticket
        from common.utils.helpers import get_delta_date, get_formatted_short_date
        from django.utils import timezone
        
        try:
            # Generate unique ticket
            ticket = new_ticket()
            while Deal.objects.filter(ticket=ticket).exists():
                ticket = new_ticket()
            
            # Get default stage (if available) - try to get by department first
            from common.models import Department
            from common.utils.helpers import get_department_id
            
            department_id = get_department_id(user)
            default_stage = None
            
            if department_id:
                default_stage = Stage.objects.filter(
                    department_id=department_id,
                    default=True
                ).first()
            
            # Fallback to any default stage
            if not default_stage:
                default_stage = Stage.objects.filter(default=True).first()
            
            # Get formatted date for workflow
            date = get_formatted_short_date()
            
            # Ensure next_step is not empty
            next_step_text = f"Review and approve {product.name} registration for {company.name}"
            if not next_step_text or len(next_step_text.strip()) == 0:
                next_step_text = "Review registration"
            
            # Truncate if too long (max 250 chars)
            if len(next_step_text) > 250:
                next_step_text = next_step_text[:247] + "..."
            
            # Ensure next_step_date is set
            next_step_date = get_delta_date(1)
            if not next_step_date:
                from datetime import date, timedelta
                next_step_date = date.today() + timedelta(days=1)
            
            # Initialize stages_dates
            stages_dates_text = ''
            if default_stage:
                stages_dates_text = f'{date} - {default_stage}\n'
            else:
                stages_dates_text = f'{date} - Registration Deal Created\n'
            
            # Create deal with all required fields
            deal = Deal(
                name=f"{product.name} - {company.name}"[:250],  # Ensure name is not too long
                next_step=next_step_text,
                next_step_date=next_step_date,
                description=f"New business registration for {product.name} service.\n\n"
                           f"Company: {company.name}\n"
                           f"Contact: {user.get_full_name() or user.username}\n"
                           f"Email: {company.email}\n"
                           f"Product: {product.name}\n\n"
                           f"Review the registration and complete the setup.",
                owner=user,
                stage=default_stage,
                ticket=ticket,
                active=True,
                relevant=True,
                is_new=True,
                workflow=f'{date} - Registration Deal Created\n',
                stages_dates=stages_dates_text,
                product=product,  # Direct link to product
            )
            
            # Set department if available
            if department_id:
                deal.department_id = department_id
                # Try to set currency from department
                try:
                    from crm.models import Currency
                    department = Department.objects.get(id=department_id)
                    if department.default_currency:
                        deal.currency = department.default_currency
                except Exception as e:
                    logger.debug(f"Could not set currency from department: {e}")
            
            # Save the deal
            deal.save()
            
            logger.info(f"Successfully created registration deal {deal.id} with ticket {ticket} for company {company.name}")
            return deal
            
        except Exception as e:
            logger.error(f"Error creating registration deal: {e}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise - let registration continue even if deal creation fails
            return None
    
    def _create_staff_message(self, user, company, product, deal):
        """Create a message visible to all staff members."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            from chat.models import ChatMessage
            from django.contrib.contenttypes.models import ContentType
            
            # Get all staff members
            staff_members = User.objects.filter(is_staff=True, is_active=True)
            
            if not staff_members.exists():
                logger.warning("No staff members found to send registration message to")
                return
            
            # Create message for the deal (so it appears in deal context)
            deal_content_type = ContentType.objects.get(app_label='crm', model='deal')
            
            message = ChatMessage.objects.create(
                content_type=deal_content_type,
                object_id=deal.id,
                content=f"New {product.name} registration: {company.name} by {user.get_full_name() or user.username}. "
                       f"Deal created: {deal.name}",
                owner=user
            )
            
            # Add all staff as recipients
            message.recipients.set(staff_members)
            message.to.set(staff_members)
            
            logger.info(f"Created staff message for registration: {company.name}")
        except Exception as e:
            logger.error(f"Error creating staff message: {e}", exc_info=True)
    
    def _notify_staff(self, user, company, product, deal):
        """Send FCM notification to all staff members."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            from fcm.services import fcm_service
            from django.contrib.auth import get_user_model
            from ecommerce.models import EcommerceCompany
            
            User = get_user_model()
            staff_members = User.objects.filter(is_staff=True, is_active=True)
            
            if not staff_members.exists():
                logger.warning("No staff members found to send FCM notification to")
                return
            
            # Try to get a system company or use the registered company for FCM context
            # FCM requires company context, so we'll use the registered company
            # Staff members should have access to view messages from this company
            
            notification_sent = 0
            for staff in staff_members:
                try:
                    # Use the registered company for FCM context
                    # This allows staff to receive notifications about new registrations
                    fcm_service.send_to_user(
                        user=staff,
                        title=f"New {product.name} Registration",
                        body=f"{company.name} registered for {product.name}. Deal: {deal.name}",
                        data={
                            'type': 'deal_created',
                            'deal_id': deal.id,
                            'company_id': str(company.id),
                            'product': product.name,
                        },
                        notification_type='deal_created',
                        company=company  # Use the registered company for FCM context
                    )
                    notification_sent += 1
                except Exception as e:
                    # Log as debug - staff might not have FCM devices registered for this company
                    logger.debug(f"Could not send FCM to staff {staff.username}: {e}")
            
            logger.info(f"Sent FCM notifications to {notification_sent}/{staff_members.count()} staff members")
        except Exception as e:
            logger.error(f"Error in _notify_staff: {e}", exc_info=True)
