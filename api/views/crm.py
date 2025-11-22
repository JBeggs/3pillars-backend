"""
CRM model viewsets.
Fail hard - explicit error handling, no silent failures.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from crm.models import Company, Contact, Deal, Lead, Request, Product, Payment
from api.serializers.crm import (
    CompanySerializer,
    ContactSerializer,
    DealSerializer,
    LeadSerializer,
    RequestSerializer,
    ProductSerializer,
    PaymentSerializer,
)
from api.permissions import IsOwnerOrReadOnly, IsDepartmentMember, IsOwnerOrCoOwner


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company model."""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsDepartmentMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'city', 'owner', 'type']
    search_fields = ['full_name', 'alternative_names', 'email', 'phone']
    ordering_fields = ['full_name', 'creation_date', 'update_date']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Filter by user's department/groups."""
        user = self.request.user
        queryset = Company.objects.all()
        
        # If user is superuser or chief, return all
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        # Filter by user's groups/department
        if user.groups.exists():
            return queryset.filter(owner__groups__in=user.groups.all())
        
        # Otherwise, only own companies
        return queryset.filter(owner=user)
    
    def perform_create(self, serializer):
        """Set owner to current user when creating company."""
        try:
            serializer.save(owner=self.request.user)
        except Exception as e:
            from django.core.exceptions import ValidationError
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f'Error creating company: {str(e)}')


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for Contact model."""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsDepartmentMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'owner', 'country']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'creation_date']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Filter by user's department/groups."""
        user = self.request.user
        queryset = Contact.objects.all()
        
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        if user.groups.exists():
            return queryset.filter(owner__groups__in=user.groups.all())
        
        return queryset.filter(owner=user)
    
    def perform_create(self, serializer):
        """Set the owner of the contact to the current user."""
        try:
            serializer.save(owner=self.request.user)
        except Exception as e:
            from django.core.exceptions import ValidationError
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f'Error creating contact: {str(e)}')


class DealViewSet(viewsets.ModelViewSet):
    """ViewSet for Deal model."""
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrCoOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'contact', 'stage', 'owner', 'co_owner', 'currency']
    search_fields = ['name', 'next_step']
    ordering_fields = ['amount', 'next_step_date', 'creation_date']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Filter deals by user access."""
        user = self.request.user
        queryset = Deal.objects.all()
        
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        # Filter by owner or co_owner
        return queryset.filter(owner=user) | queryset.filter(co_owner=user)
    
    def perform_create(self, serializer):
        """Set owner and generate unique ticket when creating deal."""
        from crm.utils.ticketproc import new_ticket
        from django.core.exceptions import ValidationError
        
        try:
            # Generate unique ticket
            ticket = new_ticket()
            while Deal.objects.filter(ticket=ticket).exists():
                ticket = new_ticket()
            
            serializer.save(owner=self.request.user, ticket=ticket)
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f'Error creating deal: {str(e)}')
    
    @action(detail=True, methods=['post'])
    def change_stage(self, request, pk=None):
        """Change deal stage."""
        deal = self.get_object()
        stage_id = request.data.get('stage_id')
        
        if not stage_id:
            return Response(
                {'error': 'stage_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from crm.models import Stage
            stage = Stage.objects.get(id=stage_id)
            deal.stage = stage
            deal.save()
            return Response({
                'status': 'stage changed',
                'stage': stage.name
            })
        except Stage.DoesNotExist:
            return Response(
                {'error': 'Stage not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error changing stage: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet for Lead model."""
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsDepartmentMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['owner', 'country', 'disqualified']
    search_fields = ['first_name', 'last_name', 'company_name', 'email', 'phone']
    ordering_fields = ['creation_date']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Filter leads by user's department."""
        user = self.request.user
        queryset = Lead.objects.all()
        
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        if user.groups.exists():
            return queryset.filter(owner__groups__in=user.groups.all())
        
        return queryset.filter(owner=user)


class RequestViewSet(viewsets.ModelViewSet):
    """ViewSet for Request model."""
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrCoOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lead_source', 'owner', 'co_owner']
    search_fields = ['name', 'email', 'subject', 'message']
    ordering_fields = ['creation_date']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Filter requests by user access."""
        user = self.request.user
        queryset = Request.objects.all()
        
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        return queryset.filter(owner=user) | queryset.filter(co_owner=user)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Product model (read-only)."""
    queryset = Product.objects.filter(on_sale=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product_category', 'currency', 'type', 'on_sale']
    search_fields = ['name', 'description']


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsDepartmentMember]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['deal', 'currency', 'status', 'payment_date']
    ordering_fields = ['payment_date', 'amount', 'creation_date']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        """Filter payments by related deal access."""
        user = self.request.user
        queryset = Payment.objects.all()
        
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        # Filter by deal owner/co_owner
        return queryset.filter(
            deal__owner=user
        ) | queryset.filter(
            deal__co_owner=user
        )

