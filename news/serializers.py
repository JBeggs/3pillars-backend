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
from .utils import get_company_from_request

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
    company = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    
    class Meta:
        model = Tag
        fields = [
            'id', 'company', 'name', 'slug', 'description', 'color',
            'usage_count', 'created_at'
        ]
        read_only_fields = ['id', 'company', 'created_at']
    
    def get_usage_count(self, obj):
        return obj.articles.count()
    
    def create(self, validated_data):
        """Auto-populate company from request context."""
        request = self.context.get('request')
        company = get_company_from_request(request)
        
        if not company:
            raise serializers.ValidationError({
                'company': 'Company is required. Please provide X-Company-Id header.'
            })
        
        validated_data['company'] = company
        
        # Auto-generate slug if not provided
        if not validated_data.get('slug') and validated_data.get('name'):
            from django.utils.text import slugify
            validated_data['slug'] = slugify(validated_data['name'])
        
        return super().create(validated_data)


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for Media."""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file = serializers.FileField(write_only=True, required=False)
    filename = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    original_filename = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mime_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    file_size = serializers.IntegerField(required=False, allow_null=True)
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
        extra_kwargs = {
            'filename': {'required': False, 'allow_blank': True},
            'mime_type': {'required': False, 'allow_blank': True},
            'original_filename': {'required': False, 'allow_blank': True},
            'file_size': {'required': False, 'allow_null': True},
        }
    
    def to_representation(self, instance):
        """Ensure file_url is always absolute."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # If file_url is relative, make it absolute
        if data.get('file_url') and not data['file_url'].startswith('http'):
            if request:
                # Use request to build absolute URI
                data['file_url'] = request.build_absolute_uri(data['file_url'])
            else:
                # Fallback: construct from settings
                from django.conf import settings
                # Try to get domain from settings
                domain = getattr(settings, 'SITE_DOMAIN', None)
                if not domain:
                    # Check ALLOWED_HOSTS for production domain
                    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
                    if allowed_hosts:
                        # Prefer PythonAnywhere domain if available
                        pythonanywhere_host = next(
                            (h for h in allowed_hosts if 'pythonanywhere.com' in h),
                            allowed_hosts[0]
                        )
                        host = pythonanywhere_host
                        # Use https for production domains, http for localhost
                        protocol = 'https' if 'pythonanywhere.com' in host or ('.' in host and 'localhost' not in host and '127.0.0.1' not in host) else 'http'
                        domain = f'{protocol}://{host}'
                    else:
                        domain = 'http://localhost:8000'
                
                # Ensure relative URL starts with /
                relative_url = data['file_url']
                if not relative_url.startswith('/'):
                    relative_url = '/' + relative_url
                
                data['file_url'] = f'{domain}{relative_url}'
        
        return data
    
    def to_internal_value(self, data):
        """Extract file and populate filename/mime_type before validation."""
        request = self.context.get('request')
        
        # Get file from request.FILES if not in data
        file = None
        if request and hasattr(request, 'FILES'):
            file = request.FILES.get('file')
        
        # If file exists, populate filename and mime_type if not provided
        if file:
            if 'filename' not in data or not data.get('filename'):
                data['filename'] = file.name
            if 'original_filename' not in data or not data.get('original_filename'):
                data['original_filename'] = file.name
            if 'mime_type' not in data or not data.get('mime_type'):
                data['mime_type'] = file.content_type or 'application/octet-stream'
            if 'file_size' not in data or not data.get('file_size'):
                data['file_size'] = file.size
        
        return super().to_internal_value(data)
    
    def validate(self, attrs):
        """Validate that file is provided and populate missing fields."""
        request = self.context.get('request')
        file = attrs.get('file')
        
        # If no file in attrs, try to get from request.FILES
        if not file and request and hasattr(request, 'FILES'):
            file = request.FILES.get('file')
            if file:
                attrs['file'] = file
        
        # If file is provided, ensure all required fields are set
        if file:
            if not attrs.get('filename'):
                attrs['filename'] = file.name
            if not attrs.get('original_filename'):
                attrs['original_filename'] = file.name
            if not attrs.get('mime_type'):
                attrs['mime_type'] = file.content_type or 'application/octet-stream'
            if not attrs.get('file_size'):
                attrs['file_size'] = file.size
        elif not attrs.get('filename') or not attrs.get('mime_type'):
            # If no file and missing required fields, raise error
            raise serializers.ValidationError({
                'file': 'File is required for media upload.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Handle file upload and generate file_path and file_url."""
        file = validated_data.pop('file', None)
        request = self.context.get('request')
        
        if not file:
            # Try to get file from request.FILES
            if request and hasattr(request, 'FILES'):
                file = request.FILES.get('file')
        
        if not file:
            raise serializers.ValidationError({'file': 'File is required for media upload.'})
        
        # Generate file path and URL
        from django.core.files.storage import default_storage
        from django.conf import settings
        
        # Save file to storage
        file_path = default_storage.save(f'media/{validated_data["filename"]}', file)
        validated_data['file_path'] = file_path
        
        # Generate absolute URL for file_url
        relative_url = default_storage.url(file_path)
        if request:
            # Use request to build absolute URI
            validated_data['file_url'] = request.build_absolute_uri(relative_url)
        else:
            # Fallback: construct absolute URL from settings
            # Try to get domain from settings or use default
            domain = getattr(settings, 'SITE_DOMAIN', None)
            if not domain:
                # Try to extract from ALLOWED_HOSTS or use default
                allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
                if allowed_hosts:
                    host = allowed_hosts[0]
                    # Use https for production domains, http for localhost
                    protocol = 'https' if 'pythonanywhere.com' in host or '.' in host else 'http'
                    domain = f'{protocol}://{host}'
                else:
                    domain = 'http://localhost:8000'
            
            validated_data['file_url'] = f'{domain}{relative_url}'
        
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


class ArticleMediaSerializer(serializers.ModelSerializer):
    """Serializer for Article Media relationship."""
    media = MediaSerializer(read_only=True)
    media_id = serializers.PrimaryKeyRelatedField(
        source='media',
        queryset=Media.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = ArticleMedia
        fields = ['id', 'article', 'media', 'media_id', 'sort_order', 'caption', 'created_at']
        read_only_fields = ['id', 'article', 'created_at']
    
    def to_internal_value(self, data):
        """Filter media queryset by company."""
        request = self.context.get('request')
        company = get_company_from_request(request)
        
        if 'media_id' in data and company:
            self.fields['media_id'].queryset = Media.objects.filter(company=company)
        
        return super().to_internal_value(data)


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for Article list view."""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    featured_media = MediaSerializer(read_only=True)
    featured_media_id = serializers.PrimaryKeyRelatedField(
        source='featured_media',
        queryset=Media.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    def to_internal_value(self, data):
        """Filter featured_media queryset by company and handle both field names."""
        request = self.context.get('request')
        company = get_company_from_request(request)
        
        # Handle both 'featured_media' and 'featured_media_id' field names
        if 'featured_media' in data and 'featured_media_id' not in data:
            data['featured_media_id'] = data.pop('featured_media')
        
        if 'featured_media_id' in data and company:
            # Update queryset to filter by company
            self.fields['featured_media_id'].queryset = Media.objects.filter(company=company)
        
        return super().to_internal_value(data)
    
    class Meta:
        model = Article
        fields = [
            'id', 'company', 'title', 'slug', 'subtitle', 'excerpt', 'status',
            'category', 'tags', 'author', 'author_name', 'featured_media', 'featured_media_id',
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
    featured_media_id = serializers.PrimaryKeyRelatedField(
        source='featured_media',
        queryset=Media.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    social_image = MediaSerializer(read_only=True)
    article_media = serializers.SerializerMethodField()
    
    def to_internal_value(self, data):
        """Filter featured_media queryset by company and handle both field names."""
        request = self.context.get('request')
        company = get_company_from_request(request)
        
        # Handle both 'featured_media' and 'featured_media_id' field names
        if 'featured_media' in data and 'featured_media_id' not in data:
            data['featured_media_id'] = data.pop('featured_media')
        
        if 'featured_media_id' in data and company:
            # Update queryset to filter by company
            self.fields['featured_media_id'].queryset = Media.objects.filter(company=company)
        
        return super().to_internal_value(data)
    
    class Meta:
        model = Article
        fields = [
            'id', 'company', 'title', 'slug', 'subtitle', 'excerpt', 'content',
            'content_type', 'featured_media', 'featured_media_id', 'social_image', 'author', 'author_name',
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
                'media': MediaSerializer(rel.media, context=self.context).data,
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
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'company', 'user', 'type', 'title', 'message',
            'related_object_type', 'related_object_id', 'is_read',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SiteSettingSerializer(serializers.ModelSerializer):
    """Serializer for Site Setting."""
    
    class Meta:
        model = SiteSetting
        fields = [
            'id', 'company', 'key', 'value', 'type', 'description',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for Team Member."""
    photo = MediaSerializer(read_only=True)
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'company', 'name', 'title', 'bio', 'photo',
            'email', 'social_links', 'sort_order', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for Testimonial."""
    photo = MediaSerializer(read_only=True)
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'company', 'name', 'title', 'company_name', 'content',
            'photo', 'rating', 'sort_order', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
