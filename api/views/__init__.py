# API views and viewsets
from api.views.auth import CustomTokenObtainPairView, register, refresh_token
from api.views.landing import MobileAppLandingView
from api.views.crm import (
    CompanyViewSet,
    ContactViewSet,
    DealViewSet,
    LeadViewSet,
    RequestViewSet,
    ProductViewSet,
    PaymentViewSet,
)
from api.views.tasks import (
    TaskViewSet,
    ProjectViewSet,
    MemoViewSet,
)

__all__ = [
    'CustomTokenObtainPairView',
    'register',
    'refresh_token',
    'CompanyViewSet',
    'ContactViewSet',
    'DealViewSet',
    'LeadViewSet',
    'RequestViewSet',
    'ProductViewSet',
    'PaymentViewSet',
    'TaskViewSet',
    'ProjectViewSet',
    'MemoViewSet',
]

