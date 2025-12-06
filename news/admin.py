"""
Admin configuration for news platform models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core.files.storage import default_storage
from django.conf import settings
from crm.site.crmadminsite import crm_site
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


class MediaAdminForm(forms.ModelForm):
    """Custom form for Media admin with file upload support."""
    file = forms.FileField(required=False, help_text='Upload a new file. Leave empty to keep existing file.')
    
    class Meta:
        model = Media
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make file required only when creating new Media
        if not self.instance.pk:
            self.fields['file'].required = True
            self.fields['file_path'].required = False
            self.fields['file_url'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        file = self.cleaned_data.get('file')
        
        if file:
            # Save file to storage
            file_path = default_storage.save(f'media/{file.name}', file)
            instance.file_path = file_path
            
            # Generate file URL
            relative_url = default_storage.url(file_path)
            # Build absolute URL
            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            if allowed_hosts:
                host = allowed_hosts[0]
                protocol = 'https' if 'pythonanywhere.com' in host or '.' in host else 'http'
                instance.file_url = f'{protocol}://{host}{relative_url}'
            else:
                instance.file_url = f'http://localhost:8000{relative_url}'
            
            # Set filename and metadata if not set
            if not instance.filename:
                instance.filename = file.name
            if not instance.original_filename:
                instance.original_filename = file.name
            if not instance.mime_type:
                instance.mime_type = file.content_type or 'application/octet-stream'
            if not instance.file_size:
                instance.file_size = file.size
            
            # Auto-detect media type from mime type
            if not instance.media_type:
                mime = instance.mime_type.lower()
                if mime.startswith('image/'):
                    instance.media_type = 'image'
                elif mime.startswith('video/'):
                    instance.media_type = 'video'
                elif mime.startswith('audio/'):
                    instance.media_type = 'audio'
                else:
                    instance.media_type = 'document'
        
        if commit:
            instance.save()
        return instance


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    form = MediaAdminForm
    list_display = ['filename', 'company', 'media_type', 'is_public', 'uploaded_by', 'created_at']
    list_filter = ['company', 'media_type', 'is_public', 'created_at']
    search_fields = ['filename', 'original_filename', 'alt_text', 'caption']
    readonly_fields = ['created_at', 'updated_at', 'file_url']
    fieldsets = (
        (None, {
            'fields': ('company', 'file', 'media_type')
        }),
        (_('File Information'), {
            'fields': ('filename', 'original_filename', 'file_path', 'file_url', 'file_size', 'mime_type'),
            'classes': ('collapse',)
        }),
        (_('Media Details'), {
            'fields': ('alt_text', 'caption', 'width', 'height', 'duration_seconds', 'uploaded_by', 'is_public')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
    readonly_fields = ['id', 'views', 'likes', 'shares', 'version', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'
    raw_id_fields = ['author', 'category', 'social_image', 'parent_version']
    filter_horizontal = ['co_authors', 'tags']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'subtitle', 'excerpt', 'content', 'content_type')
        }),
        (_('Company & Author'), {
            'fields': ('company', 'author', 'co_authors', 'category', 'tags')
        }),
        (_('Media'), {
            'fields': ('featured_media', 'social_image'),
        }),
        (_('Status & Settings'), {
            'fields': (
                'status',
                'is_premium',
                'is_breaking_news',
                'is_trending',
                'published_at',
                'scheduled_for'
            )
        }),
        (_('SEO'), {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        (_('Location'), {
            'fields': ('location_name',),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('views', 'likes', 'shares', 'read_time_minutes'),
            'classes': ('collapse',)
        }),
        (_('Versioning'), {
            'fields': ('version', 'parent_version'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter featured_media and social_image by company."""
        if db_field.name in ['featured_media', 'social_image']:
            # Get company from the article being edited
            obj = self.get_object(request, None)
            if obj and obj.company:
                kwargs['queryset'] = Media.objects.filter(company=obj.company, media_type='image').order_by('-created_at')
            else:
                # If creating new article, show all images (will be filtered after company is selected)
                kwargs['queryset'] = Media.objects.filter(media_type='image').order_by('-created_at')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        """Override form to ensure company is set before media fields."""
        form = super().get_form(request, obj, **kwargs)
        # Make company required and ensure it's set first
        if 'company' in form.base_fields:
            form.base_fields['company'].required = True
        return form


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author_name', 'author', 'is_approved', 'is_spam', 'created_at']
    list_filter = ['article__company', 'is_approved', 'is_spam', 'created_at']
    search_fields = ['content', 'author_name', 'author_email', 'article__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['article', 'author', 'parent']
    fieldsets = (
        (_('Comment'), {
            'fields': ('article', 'content', 'author_name', 'author_email', 'author', 'parent')
        }),
        (_('Moderation'), {
            'fields': ('is_approved', 'is_spam')
        }),
        (_('Metadata'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'industry', 'is_verified', 'rating', 'review_count', 'created_at']
    list_filter = ['company', 'industry', 'is_verified', 'created_at']
    search_fields = ['name', 'description', 'long_description', 'industry', 'city', 'state', 'address', 'email', 'phone']
    readonly_fields = ['id', 'rating', 'review_count', 'created_at', 'updated_at']
    raw_id_fields = ['company', 'owner', 'logo', 'cover_image']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'long_description', 'industry', 'company', 'owner')
        }),
        (_('Contact Information'), {
            'fields': ('email', 'phone', 'website_url', 'address', 'city', 'state', 'zip_code')
        }),
        (_('Media'), {
            'fields': ('logo', 'cover_image'),
            'classes': ('collapse',)
        }),
        (_('Additional Information'), {
            'fields': ('business_hours', 'social_links', 'services'),
            'classes': ('collapse',)
        }),
        (_('Verification & Status'), {
            'fields': ('is_verified',)
        }),
        (_('SEO'), {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('rating', 'review_count'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
    list_display = ['gallery', 'media', 'sort_order', 'created_at']
    list_filter = ['gallery__company', 'created_at']
    search_fields = ['gallery__title', 'media__filename']
    raw_id_fields = ['gallery', 'media']
    readonly_fields = ['created_at']


@admin.register(ArticleMedia)
class ArticleMediaAdmin(admin.ModelAdmin):
    list_display = ['article', 'media', 'sort_order', 'created_at']
    list_filter = ['article__company', 'created_at']
    search_fields = ['article__title', 'media__filename']
    raw_id_fields = ['article', 'media']
    readonly_fields = ['created_at']


@admin.register(BusinessMedia)
class BusinessMediaAdmin(admin.ModelAdmin):
    list_display = ['business', 'media', 'sort_order', 'created_at']
    list_filter = ['business__company', 'created_at']
    search_fields = ['business__name', 'media__filename']
    raw_id_fields = ['business', 'media']
    readonly_fields = ['created_at']


@admin.register(RSSArticleTracking)
class RSSArticleTrackingAdmin(admin.ModelAdmin):
    list_display = ['rss_source', 'external_id', 'article', 'created_at']
    list_filter = ['rss_source', 'created_at']
    search_fields = ['external_id', 'article__title', 'rss_source__name']
    raw_id_fields = ['rss_source', 'article']
    readonly_fields = ['created_at']


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


# Register all models to crm_site as well (for custom admin interface)
crm_site.register(Profile, ProfileAdmin)
crm_site.register(Category, CategoryAdmin)
crm_site.register(Tag, TagAdmin)
crm_site.register(Media, MediaAdmin)
crm_site.register(Gallery, GalleryAdmin)
crm_site.register(GalleryMedia, GalleryMediaAdmin)
crm_site.register(Article, ArticleAdmin)
crm_site.register(ArticleMedia, ArticleMediaAdmin)
crm_site.register(Comment, CommentAdmin)
crm_site.register(Business, BusinessAdmin)
crm_site.register(BusinessMedia, BusinessMediaAdmin)
crm_site.register(BusinessReview, BusinessReviewAdmin)
crm_site.register(Advertisement, AdvertisementAdmin)
crm_site.register(RSSSource, RSSSourceAdmin)
crm_site.register(RSSArticleTracking, RSSArticleTrackingAdmin)
crm_site.register(Notification, NotificationAdmin)
crm_site.register(SiteSetting, SiteSettingAdmin)
crm_site.register(TeamMember, TeamMemberAdmin)
crm_site.register(Testimonial, TestimonialAdmin)
crm_site.register(AudioRecording, AudioRecordingAdmin)
crm_site.register(ContentImport, ContentImportAdmin)
crm_site.register(UserSession, UserSessionAdmin)

