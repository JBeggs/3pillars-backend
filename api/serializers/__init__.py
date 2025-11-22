# Serializers for API endpoints
from api.serializers.crm import (
    CompanySerializer,
    ContactSerializer,
    DealSerializer,
    LeadSerializer,
    RequestSerializer,
    ProductSerializer,
    PaymentSerializer,
)
from api.serializers.tasks import (
    TaskSerializer,
    ProjectSerializer,
    MemoSerializer,
)
from api.serializers.auth import (
    UserSerializer,
    TokenResponseSerializer,
    RefreshTokenSerializer,
    RefreshTokenResponseSerializer,
)

__all__ = [
    'CompanySerializer',
    'ContactSerializer',
    'DealSerializer',
    'LeadSerializer',
    'RequestSerializer',
    'ProductSerializer',
    'PaymentSerializer',
    'TaskSerializer',
    'ProjectSerializer',
    'MemoSerializer',
    'UserSerializer',
    'TokenResponseSerializer',
    'RefreshTokenSerializer',
    'RefreshTokenResponseSerializer',
]

