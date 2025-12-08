from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import include
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns

from common.views.favicon import FaviconRedirect
from crm.views.contact_form import contact_form
from massmail.views.get_oauth2_tokens import get_refresh_token
from api.views.landing import MobileAppLandingView


urlpatterns = [
    path('favicon.ico', FaviconRedirect.as_view()),
    # Landing page for mobile app
    path('', MobileAppLandingView.as_view(), name='mobile_app_landing'),
    path('voip/', include('voip.urls')),
    path(
        'OAuth-2/authorize/',
        staff_member_required(get_refresh_token), 
        name='get_refresh_token'
    ),
    # API endpoints (no i18n needed)
    path('api/', include('api.urls')),
]

# Serve static files (works in both DEBUG and production for local dev)
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

# Always serve static files from STATIC_ROOT (for both DEBUG and production in local dev)
# This must be added BEFORE i18n_patterns to ensure static files are accessible
if settings.STATIC_ROOT and hasattr(settings.STATIC_ROOT, 'exists') and settings.STATIC_ROOT.exists():
    urlpatterns += [
        re_path(
            r'^static/(?P<path>.*)$',
            serve,
            {'document_root': str(settings.STATIC_ROOT)},
        ),
    ]

# Add staticfiles URL patterns (serves from STATICFILES_DIRS and app static folders)
# This only works when DEBUG=True
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

# Serve media files (only in DEBUG mode)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls'))
    ]

urlpatterns += i18n_patterns(
    path(settings.SECRET_CRM_PREFIX, include('common.urls')),
    path(settings.SECRET_CRM_PREFIX, include('crm.urls')),
    path(settings.SECRET_CRM_PREFIX, include('massmail.urls')),
    path(settings.SECRET_CRM_PREFIX, include('tasks.urls')),
    path(settings.SECRET_ADMIN_PREFIX, admin.site.urls),
    path('contact-form/<uuid:uuid>/', contact_form, name='contact_form'),
)
