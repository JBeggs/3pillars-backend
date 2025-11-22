"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.views.auth import CustomTokenObtainPairView, refresh_token, list_users
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
from api.views.chat import ChatMessageViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'deals', DealViewSet, basename='deal')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'requests', RequestViewSet, basename='request')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'memos', MemoViewSet, basename='memo')
router.register(r'chat', ChatMessageViewSet, basename='chat')

urlpatterns = [
    # Authentication (specific paths first)
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', refresh_token, name='register'),  # Placeholder
    path('auth/users/', list_users, name='list_users'),
    
    # API Documentation (specific paths)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API routes (router URLs - matches /api/companies/, /api/tasks/, etc.)
    path('', include(router.urls)),
]

