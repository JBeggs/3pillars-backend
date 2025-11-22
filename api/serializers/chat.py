"""
Chat model serializers.
"""
from rest_framework import serializers
from chat.models import ChatMessage
from django.contrib.contenttypes.models import ContentType
from common.models import TheFile


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    recipients_usernames = serializers.SerializerMethodField()
    file_urls = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'content', 'owner', 'owner_username',
            'content_type', 'content_type_name', 'object_id',
            'answer_to', 'topic', 'recipients', 'recipients_usernames',
            'file_urls', 'creation_date'
        ]
        read_only_fields = ['id', 'creation_date']
        extra_kwargs = {
            'content_type': {'required': False, 'allow_null': True},
            'object_id': {'required': False, 'allow_null': True},
            'answer_to': {'required': False, 'allow_null': True},
            'topic': {'required': False, 'allow_null': True},
            'recipients': {'required': False, 'allow_empty': True},
        }
    
    def get_recipients_usernames(self, obj) -> list[str]:
        """Return list of recipient usernames."""
        return [user.username for user in obj.recipients.all()]
    
    def get_file_urls(self, obj) -> list[dict]:
        """Return list of file URLs attached to this message."""
        from django.conf import settings
        files = TheFile.objects.filter(
            content_type=ContentType.objects.get_for_model(ChatMessage),
            object_id=obj.id
        )
        result = []
        for file in files:
            if file.file:
                # Construct full URL
                file_url = file.file.url
                if not file_url.startswith('http'):
                    # Relative URL - make it absolute
                    request = self.context.get('request')
                    if request:
                        file_url = request.build_absolute_uri(file_url)
                    else:
                        # Fallback: construct from settings
                        file_url = f"{settings.MEDIA_URL}{file.file.name}"
                
                result.append({
                    'id': file.id,
                    'url': file_url,
                    'name': file.file.name.split('/')[-1],
                })
        return result
    
    def validate(self, data):
        """Validate chat message data."""
        # If content_type and object_id are provided, validate they exist
        if 'content_type' in data and 'object_id' in data:
            content_type = data.get('content_type')
            object_id = data.get('object_id')
            if content_type and object_id:
                try:
                    model_class = content_type.model_class()
                    if model_class:
                        model_class.objects.get(pk=object_id)
                except Exception:
                    raise serializers.ValidationError({
                        'object_id': f'Object with id {object_id} does not exist for content type {content_type}.'
                    })
        return data

