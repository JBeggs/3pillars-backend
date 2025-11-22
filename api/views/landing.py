"""
Landing page view for the Flutter mobile app.
"""
from django.views.generic import TemplateView


class MobileAppLandingView(TemplateView):
    """Landing page showcasing the Flutter mobile app benefits."""
    template_name = 'api/landing.html'

