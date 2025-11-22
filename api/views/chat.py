"""
Chat model viewsets.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType

from chat.models import ChatMessage
from api.serializers.chat import ChatMessageSerializer
from api.permissions import IsDepartmentMember
from common.models import TheFile
from django.conf import settings


class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for ChatMessage model."""
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated, IsDepartmentMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type', 'object_id', 'owner']
    search_fields = ['content']
    ordering_fields = ['creation_date']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Filter messages by user access."""
        user = self.request.user
        queryset = ChatMessage.objects.all()
        
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        # Filter messages where user is owner or recipient
        return queryset.filter(owner=user) | queryset.filter(recipients=user) | queryset.filter(to=user)
    
    def create(self, request, *args, **kwargs):
        """Create chat message with optional file attachments."""
        # Handle multipart form data
        data = request.data.copy()
        files = request.FILES.getlist('files')  # Support multiple files
        
        # Create the message
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(owner=request.user)
        
        # Attach files to the message
        if files:
            message_content_type = ContentType.objects.get_for_model(ChatMessage)
            for file in files:
                TheFile.objects.create(
                    file=file,
                    content_type=message_content_type,
                    object_id=message.id
                )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """Set the owner of the message to the current user."""
        try:
            serializer.save(owner=self.request.user)
        except Exception as e:
            from django.core.exceptions import ValidationError
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f'Error creating message: {str(e)}')
    
    @action(detail=False, methods=['get'])
    def for_object(self, request):
        """Get messages for a specific object (task, deal, etc.)."""
        content_type_id = request.query_params.get('content_type_id')
        object_id = request.query_params.get('object_id')
        
        if not content_type_id or not object_id:
            return Response(
                {'error': 'content_type_id and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
            messages = ChatMessage.objects.filter(
                content_type=content_type,
                object_id=object_id
            ).order_by('creation_date')
            
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
        except ContentType.DoesNotExist:
            return Response(
                {'error': 'Invalid content_type_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

