"""
CRM model serializers.
Fail hard - explicit field definitions, no silent errors.
"""
from rest_framework import serializers
from crm.models import Company, Contact, Deal, Lead, Request, Product, Payment


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    city_name_display = serializers.CharField(source='city_name', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'full_name', 'alternative_names', 'website', 'phone', 'email',
            'registration_number', 'country', 'country_name', 'city', 'city_name_display',
            'type', 'type_name', 'owner', 'owner_username', 'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']
        extra_kwargs = {
            'alternative_names': {'required': False, 'allow_blank': True},
            'website': {'required': False, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
            'registration_number': {'required': False, 'allow_blank': True},
            'country': {'required': False, 'allow_null': True},
            'city': {'required': False, 'allow_null': True},
            'type': {'required': False, 'allow_null': True},
        }
    
    def validate(self, data):
        """Validate company data."""
        # Ensure alternative_names defaults to empty string if not provided
        if 'alternative_names' not in data:
            data['alternative_names'] = ''
        if 'website' not in data:
            data['website'] = ''
        if 'phone' not in data:
            data['phone'] = ''
        if 'email' not in data:
            data['email'] = ''
        if 'registration_number' not in data:
            data['registration_number'] = ''
        
        return data


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for Contact model."""
    company_name = serializers.CharField(source='company.full_name', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'middle_name', 'last_name', 'full_name',
            'title', 'phone', 'email', 'secondary_email',
            'company', 'company_name', 'country', 'country_name',
            'owner', 'owner_username', 'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']
        extra_kwargs = {
            'middle_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'title': {'required': False, 'allow_null': True, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
            'secondary_email': {'required': False, 'allow_blank': True},
            'country': {'required': False, 'allow_null': True},
        }
    
    def validate(self, data):
        """Set defaults for optional fields if not provided."""
        # Set default email if not provided (required field but can be empty string)
        if 'email' not in data or not data.get('email'):
            data['email'] = ''
        # Set default middle_name if not provided
        if 'middle_name' not in data or not data.get('middle_name'):
            data['middle_name'] = ''
        # Set default last_name if not provided
        if 'last_name' not in data or not data.get('last_name'):
            data['last_name'] = ''
        # Set default phone if not provided
        if 'phone' not in data or not data.get('phone'):
            data['phone'] = ''
        # Set default secondary_email if not provided
        if 'secondary_email' not in data or not data.get('secondary_email'):
            data['secondary_email'] = ''
        return data
    
    def get_full_name(self, obj) -> str:
        """Return full name of contact."""
        parts = [obj.first_name]
        if obj.middle_name:
            parts.append(obj.middle_name)
        if obj.last_name:
            parts.append(obj.last_name)
        return ' '.join(parts)


class DealSerializer(serializers.ModelSerializer):
    """Serializer for Deal model."""
    company_name = serializers.CharField(source='company.full_name', read_only=True)
    contact_name = serializers.SerializerMethodField()
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    co_owner_username = serializers.CharField(source='co_owner.username', read_only=True)
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    currency_code = serializers.CharField(source='currency.name', read_only=True)
    
    class Meta:
        model = Deal
        fields = [
            'id', 'name', 'company', 'company_name', 'contact', 'contact_name',
            'amount', 'currency', 'currency_code', 'stage', 'stage_name',
            'owner', 'owner_username', 'co_owner', 'co_owner_username',
            'next_step', 'next_step_date', 'description', 'workflow',
            'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']
        extra_kwargs = {
            'next_step': {'required': False, 'allow_blank': True},
            'next_step_date': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_blank': True},
            'workflow': {'required': False, 'allow_blank': True},
            'company': {'required': False, 'allow_null': True},
            'contact': {'required': False, 'allow_null': True},
            'stage': {'required': False, 'allow_null': True},
            'amount': {'required': False, 'allow_null': True},
            'currency': {'required': False, 'allow_null': True},
            'co_owner': {'required': False, 'allow_null': True},
        }
    
    def validate(self, data):
        """Set defaults for next_step and next_step_date if not provided."""
        from common.utils.helpers import get_delta_date
        
        # Set default next_step if not provided
        if 'next_step' not in data or not data.get('next_step'):
            data['next_step'] = ''
        
        # Set default next_step_date if not provided
        if 'next_step_date' not in data or data.get('next_step_date') is None:
            data['next_step_date'] = get_delta_date(1)
        
        # Set defaults for optional fields
        if 'description' not in data:
            data['description'] = ''
        if 'workflow' not in data:
            data['workflow'] = ''
        
        return data
    
    def get_contact_name(self, obj) -> str | None:
        """Return contact full name if exists."""
        if obj.contact:
            return f"{obj.contact.first_name} {obj.contact.last_name}".strip()
        return None


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for Lead model."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'middle_name', 'last_name', 'full_name',
            'company_name', 'website', 'company_phone', 'company_email',
            'phone', 'email', 'country', 'country_name',
            'disqualified', 'owner', 'owner_username',
            'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']
    
    def get_full_name(self, obj) -> str:
        """Return full name of lead."""
        parts = [obj.first_name]
        if obj.middle_name:
            parts.append(obj.middle_name)
        if obj.last_name:
            parts.append(obj.last_name)
        return ' '.join(parts)


class RequestSerializer(serializers.ModelSerializer):
    """Serializer for Request model."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    co_owner_username = serializers.CharField(source='co_owner.username', read_only=True, allow_null=True)
    lead_source_name = serializers.CharField(source='lead_source.name', read_only=True, allow_null=True)
    company_name_display = serializers.CharField(source='company_name', read_only=True)
    contact_name = serializers.CharField(source='contact.first_name', read_only=True, allow_null=True)
    deal_name = serializers.CharField(source='deal.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Request
        fields = [
            'id', 'request_for', 'first_name', 'middle_name', 'last_name',
            'email', 'phone', 'website', 'company_name', 'company_name_display',
            'lead_source', 'lead_source_name',
            'company', 'contact', 'contact_name', 'deal', 'deal_name',
            'country', 'city', 'city_name',
            'description', 'translation', 'remark',
            'receipt_date', 'pending', 'subsequent',
            'owner', 'owner_username', 'co_owner', 'co_owner_username',
            'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    category_name = serializers.CharField(source='product_category.name', read_only=True, allow_null=True)
    currency_code = serializers.CharField(source='currency.name', read_only=True, allow_null=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'currency', 'currency_code',
            'product_category', 'category_name', 'type', 'type_display',
            'on_sale', 'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    deal_name = serializers.CharField(source='deal.name', read_only=True)
    currency_code = serializers.CharField(source='currency.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'deal', 'deal_name', 'amount', 'currency', 'currency_code',
            'payment_date', 'status', 'status_display',
            'contract_number', 'invoice_number', 'order_number',
            'through_representation'
        ]
        read_only_fields = ['id']

