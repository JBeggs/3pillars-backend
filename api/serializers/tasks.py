"""
Tasks model serializers.
Fail hard - explicit field definitions, no silent errors.
"""
from rest_framework import serializers
from tasks.models import Task, Project, Memo


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    responsible_usernames = serializers.SerializerMethodField()
    co_owner_username = serializers.CharField(source='co_owner.username', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'note',
            'owner', 'owner_username', 'co_owner', 'co_owner_username',
            'project', 'project_name', 'stage', 'stage_name',
            'responsible', 'responsible_usernames',
            'priority', 'priority_display',
            'due_date', 'start_date', 'closing_date', 'lead_time',
            'next_step', 'next_step_date', 'active',
            'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']
        extra_kwargs = {
            'next_step': {'required': False, 'allow_blank': True},
            'next_step_date': {'required': False, 'allow_null': True},
            'stage': {'required': False, 'allow_null': True},
        }
    
    def validate(self, data):
        """Set defaults for required fields if not provided."""
        from common.utils.helpers import get_delta_date
        from tasks.models import TaskStage
        from rest_framework.exceptions import ValidationError
        
        # Set default stage if not provided (use default stage)
        # This is required because Task.stage is a required ForeignKey
        if 'stage' not in data or data.get('stage') is None:
            default_stage = TaskStage.objects.filter(default=True).first()
            if not default_stage:
                # Fallback to first available stage
                default_stage = TaskStage.objects.first()
            if default_stage:
                data['stage'] = default_stage  # Assign the instance, not the ID
            else:
                # If no stages exist, raise validation error with helpful message
                raise ValidationError({
                    'stage': 'No task stages available. Please run "python manage.py loaddata tasks/fixtures/taskstage.json" to create default stages.'
                })
        # If stage is provided as an integer ID, convert it to the instance
        elif isinstance(data.get('stage'), int):
            stage_id = data['stage']
            try:
                stage_instance = TaskStage.objects.get(pk=stage_id)
                data['stage'] = stage_instance
            except TaskStage.DoesNotExist:
                raise ValidationError({
                    'stage': f'TaskStage with id {stage_id} does not exist.'
                })
        
        # Set default next_step if not provided
        if 'next_step' not in data or not data.get('next_step'):
            data['next_step'] = ''
        
        # Set default next_step_date if not provided
        if 'next_step_date' not in data or data.get('next_step_date') is None:
            data['next_step_date'] = get_delta_date(1)
        
        # Set default priority if not provided (default is 2 = Middle)
        if 'priority' not in data or data.get('priority') is None:
            data['priority'] = 2
        
        return data
    
    def get_responsible_usernames(self, obj) -> list[str]:
        """Return list of responsible user usernames."""
        return [user.username for user in obj.responsible.all()]


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    co_owner_username = serializers.CharField(source='co_owner.username', read_only=True)
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'note',
            'owner', 'owner_username', 'co_owner', 'co_owner_username',
            'stage', 'stage_name',
            'next_step', 'next_step_date', 'active',
            'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']


class MemoSerializer(serializers.ModelSerializer):
    """Serializer for Memo model."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    to_username = serializers.CharField(source='to.username', read_only=True)
    task_name = serializers.CharField(source='task.name', read_only=True, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    deal_name = serializers.CharField(source='deal.name', read_only=True, allow_null=True)
    resolution_name = serializers.CharField(source='resolution.name', read_only=True, allow_null=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    
    class Meta:
        model = Memo
        fields = [
            'id', 'name', 'description', 'note',
            'owner', 'owner_username',
            'to', 'to_username',
            'task', 'task_name',
            'project', 'project_name',
            'deal', 'deal_name',
            'resolution', 'resolution_name',
            'stage', 'stage_display',
            'draft', 'notified',
            'review_date',
            'creation_date', 'update_date'
        ]
        read_only_fields = ['id', 'creation_date', 'update_date']

