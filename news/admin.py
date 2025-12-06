"""
Admin configuration for news platform models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
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


@admin.register(GalleryMedia)
class GalleryMediaAdmin(admin.ModelAdmin):
    list_display = ['gallery', 'media', 'order', 'created_at']
    list_filter = ['gallery__company', 'created_at']
    search_fields = ['gallery__title', 'media__filename']
    raw_id_fields = ['gallery', 'media']
    readonly_fields = ['created_at']


@admin.register(ArticleMedia)
class ArticleMediaAdmin(admin.ModelAdmin):
    list_display = ['article', 'media', 'order', 'is_featured', 'created_at']
    list_filter = ['article__company', 'is_featured', 'created_at']
    search_fields = ['article__title', 'media__filename']
    raw_id_fields = ['article', 'media']
    readonly_fields = ['created_at']


@admin.register(BusinessMedia)
class BusinessMediaAdmin(admin.ModelAdmin):
    list_display = ['business', 'media', 'order', 'is_featured', 'created_at']
    list_filter = ['business__company', 'is_featured', 'created_at']
    search_fields = ['business__name', 'media__filename']
    raw_id_fields = ['business', 'media']
    readonly_fields = ['created_at']


@admin.register(RSSArticleTracking)
class RSSArticleTrackingAdmin(admin.ModelAdmin):
    list_display = ['rss_source', 'article', 'imported_at', 'status']
    list_filter = ['rss_source__company', 'status', 'imported_at']
    search_fields = ['rss_source__name', 'article__title', 'external_id']
    raw_id_fields = ['rss_source', 'article']
    readonly_fields = ['imported_at']


@admin.register(AudioRecording)
class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'audio_url', 'duration_seconds', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['user__username', 'user__email', 'audio_url', 'transcription']
    raw_id_fields = ['user', 'company', 'media']
    readonly_fields = ['created_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'company', 'media', 'audio_url')
        }),
        (_('Transcription'), {
            'fields': ('transcription', 'duration_seconds'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContentImport)
class ContentImportAdmin(admin.ModelAdmin):
    list_display = ['company', 'filename', 'status', 'imported_articles', 'total_articles', 'created_at']
    list_filter = ['company', 'status', 'created_at']
    search_fields = ['filename', 'file_url', 'error_message']
    raw_id_fields = ['user', 'company']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'company', 'filename', 'file_url', 'status')
        }),
        (_('Import Progress'), {
            'fields': ('imported_articles', 'total_articles', 'error_message'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('metadata', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'ip_address', 'started_at', 'ended_at', 'page_views']
    list_filter = ['started_at', 'ended_at']
    search_fields = ['user__username', 'user__email', 'session_id', 'ip_address']
    raw_id_fields = ['user']
    readonly_fields = ['started_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'session_id', 'ip_address', 'user_agent')
        }),
        (_('Session Data'), {
            'fields': ('started_at', 'ended_at', 'page_views'),
            'classes': ('collapse',)
        }),
    )

