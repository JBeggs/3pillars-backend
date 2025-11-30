"""
URL configuration for news platform API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, TagViewSet, MediaViewSet, GalleryViewSet,
    ArticleViewSet, CommentViewSet, BusinessViewSet, BusinessReviewViewSet,
    AdvertisementViewSet, RSSSourceViewSet, NotificationViewSet,
    SiteSettingViewSet, TeamMemberViewSet, TestimonialViewSet,
    ProfileViewSet, StatsViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'media', MediaViewSet, basename='media')
router.register(r'galleries', GalleryViewSet, basename='gallery')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'business-reviews', BusinessReviewViewSet, basename='business-review')
router.register(r'advertisements', AdvertisementViewSet, basename='advertisement')
router.register(r'rss-sources', RSSSourceViewSet, basename='rss-source')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'site-settings', SiteSettingViewSet, basename='site-setting')
router.register(r'team-members', TeamMemberViewSet, basename='team-member')
router.register(r'testimonials', TestimonialViewSet, basename='testimonial')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]

