"""
Serializers for news platform API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Profile, Category, Tag, Media, Gallery, GalleryMedia,
    Article, ArticleMedia, Comment, Business, BusinessMedia,
    BusinessReview, Advertisement, RSSSource, RSSArticleTracking,
    Notification, SiteSetting, TeamMember, Testimonial,
    AudioRecording, ContentImport, UserSession
)

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for News Profile."""
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'user', 'email', 'username', 'full_name', 'bio', 'avatar_url',
            'role', 'is_verified', 'social_links', 'preferences',
            'last_seen_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category."""
    article_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'company', 'name', 'slug', 'description', 'color',
            'parent', 'sort_order', 'is_featured', 'article_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_article_count(self, obj):
        return obj.articles.count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag."""
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = [
            'id', 'company', 'name', 'slug', 'description', 'color',
            'usage_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_usage_count(self, obj):
        return obj.articles.count()


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for Media."""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file = serializers.FileField(write_only=True, required=False)
    filename = serializers.CharField(required=False, allow_blank=True)
    mime_type = serializers.CharField(required=False, allow_blank=True)
    company = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    
    class Meta:
        model = Media
        fields = [
            'id', 'company', 'file', 'filename', 'original_filename', 'file_path', 'file_url',
            'file_size', 'mime_type', 'media_type', 'width', 'height', 'duration_seconds',
            'alt_text', 'caption', 'uploaded_by', 'uploaded_by_name', 'is_public',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'company', 'file_path', 'file_url', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate that file is provided if filename/mime_type are not."""
        request = self.context.get('request')
        file = attrs.get('file')
        
        # If no file in attrs, try to get from request.FILES
        if not file and request and hasattr(request, 'FILES'):
            file = request.FILES.get('file')
            if file:
                attrs['file'] = file
        
        # If file is provided, generate filename and mime_type if missing
        if file:
            if not attrs.get('filename'):
                attrs['filename'] = file.name
            if not attrs.get('original_filename'):
                attrs['original_filename'] = file.name
            if not attrs.get('mime_type'):
                attrs['mime_type'] = file.content_type or 'application/octet-stream'
            if not attrs.get('file_size'):
                attrs['file_size'] = file.size
        
        return attrs
    
    def create(self, validated_data):
        """Handle file upload and generate file_path and file_url."""
        file = validated_data.pop('file', None)
        if not file:
            # Try to get file from request.FILES
            request = self.context.get('request')
            if request and hasattr(request, 'FILES'):
                file = request.FILES.get('file')
        
        if not file:
            raise serializers.ValidationError({'file': 'File is required for media upload.'})
        
        # Generate file path and URL
        from django.core.files.storage import default_storage
        
        # Save file to storage
        file_path = default_storage.save(f'media/{validated_data["filename"]}', file)
        validated_data['file_path'] = file_path
        validated_data['file_url'] = default_storage.url(file_path)
        
        return super().create(validated_data)


class GalleryMediaSerializer(serializers.ModelSerializer):
    """Serializer for Gallery Media."""
    media = MediaSerializer(read_only=True)
    
    class Meta:
        model = GalleryMedia
        fields = ['id', 'gallery', 'media', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class GallerySerializer(serializers.ModelSerializer):
    """Serializer for Gallery."""
    cover_image = MediaSerializer(read_only=True)
    items = GalleryMediaSerializer(source='gallery_items', many=True, read_only=True)
    
    class Meta:
        model = Gallery
        fields = [
            'id', 'company', 'title', 'description', 'slug', 'cover_image',
            'created_by', 'is_public', 'sort_order', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for Article list view."""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    featured_media = MediaSerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'company', 'title', 'slug', 'subtitle', 'excerpt', 'status',
            'category', 'tags', 'author', 'author_name', 'featured_media',
            'is_premium', 'is_breaking_news', 'is_trending',
            'views', 'likes', 'shares', 'read_time_minutes',
            'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'views', 'likes', 'shares', 'created_at', 'updated_at']


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer for Article detail view."""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    featured_media = MediaSerializer(read_only=True)
    social_image = MediaSerializer(read_only=True)
    article_media = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'company', 'title', 'slug', 'subtitle', 'excerpt', 'content',
            'content_type', 'featured_media', 'social_image', 'author', 'author_name',
            'co_authors', 'category', 'tags', 'status', 'is_premium',
            'is_breaking_news', 'is_trending', 'seo_title', 'seo_description',
            'views', 'likes', 'shares', 'read_time_minutes', 'published_at',
            'scheduled_for', 'location_name', 'version', 'parent_version',
            'article_media', 'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = [
            'id', 'views', 'likes', 'shares', 'version', 'created_at', 'updated_at'
        ]
    
    def get_article_media(self, obj):
        """Get article media relations."""
        media_relations = obj.article_media_relations.all().order_by('sort_order')
        return [
            {
                'id': str(rel.media.id),
                'media': MediaSerializer(rel.media).data,
                'sort_order': rel.sort_order,
                'caption': rel.caption
            }
            for rel in media_relations
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment."""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'parent', 'author', 'author_name', 'author_email',
            'content', 'is_approved', 'is_spam', 'replies',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """Get nested replies."""
        replies = obj.replies.filter(is_approved=True).order_by('created_at')
        return CommentSerializer(replies, many=True).data


class BusinessListSerializer(serializers.ModelSerializer):
    """Serializer for Business list view."""
    logo = MediaSerializer(read_only=True)
    cover_image = MediaSerializer(read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Business
        fields = [
            'id', 'company', 'name', 'slug', 'description', 'industry',
            'logo', 'cover_image', 'owner', 'owner_name',
            'is_verified', 'rating', 'review_count',
            'city', 'state', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rating', 'review_count', 'created_at', 'updated_at']


class BusinessDetailSerializer(serializers.ModelSerializer):
    """Serializer for Business detail view."""
    logo = MediaSerializer(read_only=True)
    cover_image = MediaSerializer(read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = [
            'id', 'company', 'name', 'slug', 'description', 'long_description',
            'industry', 'website_url', 'phone', 'email', 'address', 'city',
            'state', 'zip_code', 'logo', 'cover_image', 'owner', 'owner_name',
            'business_hours', 'social_links', 'services', 'is_verified',
            'rating', 'review_count', 'seo_title', 'seo_description',
            'reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rating', 'review_count', 'created_at', 'updated_at']
    
    def get_reviews(self, obj):
        """Get approved reviews."""
        reviews = obj.reviews.filter(is_approved=True).order_by('-created_at')[:10]
        return BusinessReviewSerializer(reviews, many=True).data


class BusinessReviewSerializer(serializers.ModelSerializer):
    """Serializer for Business Review."""
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    
    class Meta:
        model = BusinessReview
        fields = [
            'id', 'business', 'reviewer', 'reviewer_name', 'reviewer_email',
            'rating', 'title', 'comment', 'is_verified', 'is_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer for Advertisement."""
    image = MediaSerializer(read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    
    class Meta:
        model = Advertisement
        fields = [
            'id', 'business', 'business_name', 'title', 'description',
            'image', 'image_url', 'link_url', 'position', 'status',
            'impressions', 'clicks', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'impressions', 'clicks', 'created_at', 'updated_at']


class RSSSourceSerializer(serializers.ModelSerializer):
    """Serializer for RSS Source."""
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = RSSSource
        fields = [
            'id', 'company', 'name', 'url', 'category', 'status',
            'last_fetched_at', 'last_error', 'fetch_interval_minutes',
            'max_articles_per_fetch', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_fetched_at', 'last_error', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification."""
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'company', 'type', 'title', 'message', 'data',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SiteSettingSerializer(serializers.ModelSerializer):
    """Serializer for Site Setting."""
    class Meta:
        model = SiteSetting
        fields = [
            'id', 'company', 'key', 'value', 'description', 'type',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for Team Member."""
    image = MediaSerializer(read_only=True)
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'company', 'name', 'title', 'bio', 'email', 'image',
            'social_links', 'is_featured', 'sort_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for Testimonial."""
    image = MediaSerializer(read_only=True)
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'company', 'name', 'title', 'company_name', 'content',
            'image', 'rating', 'is_featured', 'sort_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

