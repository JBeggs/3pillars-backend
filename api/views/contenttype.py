"""
ContentType API views.
Provides ContentType IDs for Flutter app.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_content_type_id(request):
    """
    Get ContentType ID for a model.
    
    Query params:
    - app_label: App label (e.g., 'tasks', 'crm')
    - model: Model name (e.g., 'task', 'deal')
    
    Returns:
    - id: ContentType ID
    """
    app_label = request.query_params.get('app_label')
    model = request.query_params.get('model')
    
    if not app_label or not model:
        return Response(
            {'error': 'app_label and model are required'},
            status=400
        )
    
    try:
        content_type = ContentType.objects.get(
            app_label=app_label,
            model=model
        )
        return Response({
            'id': content_type.id,
            'app_label': content_type.app_label,
            'model': content_type.model,
        })
    except ContentType.DoesNotExist:
        return Response(
            {'error': f'ContentType not found for {app_label}.{model}'},
            status=404
        )

