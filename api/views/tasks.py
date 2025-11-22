"""
Tasks model viewsets.
Fail hard - explicit error handling, no silent failures.
"""
import logging
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from tasks.models import Task, Project, Memo
from api.serializers.tasks import (
    TaskSerializer,
    ProjectSerializer,
    MemoSerializer,
)
from api.permissions import IsResponsibleOrOwner, IsOwnerOrReadOnly, IsDepartmentMember, IsOwnerOrCoOwner

logger = logging.getLogger(__name__)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task model."""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsResponsibleOrOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'stage', 'owner', 'co_owner', 'priority', 'active']
    search_fields = ['name', 'description', 'next_step']
    ordering_fields = ['due_date', 'priority', 'creation_date']
    ordering = ['due_date', '-priority']
    
    def get_queryset(self):
        """Filter tasks by user access."""
        user = self.request.user
        queryset = Task.objects.all()
        
        # Filter by query params
        assigned_to_me = self.request.query_params.get('assigned_to_me', None)
        created_by_me = self.request.query_params.get('created_by_me', None)
        
        if assigned_to_me == 'true':
            # Tasks where user is responsible
            queryset = queryset.filter(responsible=user)
        elif created_by_me == 'true':
            # Tasks created by user
            queryset = queryset.filter(owner=user)
        else:
            # Default: show tasks where user is owner, co_owner, or responsible
            if not (user.is_superuser or getattr(user, 'is_chief', False)):
                queryset = queryset.filter(
                    owner=user
                ) | queryset.filter(
                    co_owner=user
                ) | queryset.filter(
                    responsible=user
                )
        
        return queryset.distinct()
    
    def create(self, request, *args, **kwargs):
        """Override create to log validation errors."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f'Task creation validation failed: {serializer.errors}')
            logger.error(f'Request data: {request.data}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f'Error creating task: {str(e)}', exc_info=True)
            logger.error(f'Validated data: {serializer.validated_data}')
            return Response(
                {'error': f'Error creating task: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        """Set owner to current user when creating task."""
        task = serializer.save(owner=self.request.user)
        # Responsible users are handled by the serializer's many-to-many field
        return task
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark task as complete."""
        task = self.get_object()
        
        try:
            from tasks.models import TaskStage
            # Find done stage
            done_stage = TaskStage.objects.filter(done=True).first()
            if not done_stage:
                return Response(
                    {'error': 'No done stage configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            task.stage = done_stage
            task.active = False
            task.save()
            
            return Response({
                'status': 'task completed',
                'task_id': task.id
            })
        except Exception as e:
            return Response(
                {'error': f'Error completing task: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Project model."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrCoOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['owner', 'co_owner', 'stage', 'active']
    search_fields = ['name', 'description']
    ordering_fields = ['creation_date']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Filter projects by user access."""
        user = self.request.user
        queryset = Project.objects.all()
        
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        return queryset.filter(owner=user) | queryset.filter(co_owner=user)


class MemoViewSet(viewsets.ModelViewSet):
    """ViewSet for Memo model."""
    queryset = Memo.objects.all()
    serializer_class = MemoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['owner']
    search_fields = ['name', 'content']
    ordering_fields = ['creation_date']
    ordering = ['-creation_date']
    
    def get_queryset(self):
        """Filter memos by user access."""
        user = self.request.user
        queryset = Memo.objects.all()
        
        if user.is_superuser or getattr(user, 'is_chief', False):
            return queryset
        
        return queryset.filter(owner=user)

