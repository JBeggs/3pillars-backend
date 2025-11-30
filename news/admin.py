"""
Admin configuration for news platform models.
"""
from django.contrib import admin
from .models import (
    Profile, Category, Tag, Media, Gallery, GalleryMedia,
    Article, ArticleMedia, Comment, Business, BusinessMedia,
    BusinessReview, Advertisement, RSSSource, RSSArticleTracking,
    Notification, SiteSetting, TeamMember, Testimonial,
    AudioRecording, ContentImport, UserSession
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'created_at']
    search_fields = ['user__email', 'full_name', 'username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'slug', 'is_featured', 'sort_order', 'created_at']
    list_filter = ['company', 'is_featured', 'created_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'slug', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at']


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['filename', 'company', 'media_type', 'is_public', 'uploaded_by', 'created_at']
    list_filter = ['company', 'media_type', 'is_public', 'created_at']
    search_fields = ['filename', 'original_filename', 'alt_text', 'caption']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'slug', 'is_public', 'created_by', 'created_at']
    list_filter = ['company', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'slug']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'author', 'status', 'is_premium', 'views', 'published_at', 'created_at']
    list_filter = ['company', 'status', 'is_premium', 'is_breaking_news', 'is_trending', 'created_at']
    search_fields = ['title', 'subtitle', 'excerpt', 'content']
    readonly_fields = ['views', 'likes', 'shares', 'version', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author_name', 'author', 'is_approved', 'is_spam', 'created_at']
    list_filter = ['is_approved', 'is_spam', 'created_at']
    search_fields = ['content', 'author_name', 'author_email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'industry', 'is_verified', 'rating', 'review_count', 'created_at']
    list_filter = ['company', 'industry', 'is_verified', 'created_at']
    search_fields = ['name', 'description', 'industry', 'city', 'state']
    readonly_fields = ['rating', 'review_count', 'created_at', 'updated_at']


@admin.register(BusinessReview)
class BusinessReviewAdmin(admin.ModelAdmin):
    list_display = ['business', 'reviewer_name', 'reviewer', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'is_verified', 'rating', 'created_at']
    search_fields = ['title', 'comment', 'reviewer_name', 'reviewer_email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'business', 'position', 'status', 'impressions', 'clicks', 'created_at']
    list_filter = ['position', 'status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['impressions', 'clicks', 'created_at', 'updated_at']


@admin.register(RSSSource)
class RSSSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'status', 'last_fetched_at', 'created_at']
    list_filter = ['company', 'status', 'created_at']
    search_fields = ['name', 'url']
    readonly_fields = ['last_fetched_at', 'last_error', 'created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'type', 'title', 'is_read', 'created_at']
    list_filter = ['company', 'type', 'is_read', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'company', 'type', 'is_public', 'updated_at']
    list_filter = ['company', 'type', 'is_public', 'created_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'title', 'is_featured', 'sort_order', 'created_at']
    list_filter = ['company', 'is_featured', 'created_at']
    search_fields = ['name', 'title', 'bio', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'company_name', 'rating', 'is_featured', 'created_at']
    list_filter = ['company', 'is_featured', 'rating', 'created_at']
    search_fields = ['name', 'title', 'company_name', 'content']
    readonly_fields = ['created_at', 'updated_at']

