"""
News platform models for The Riverside Herald.
All models are tenant-scoped via EcommerceCompany.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class Profile(models.Model):
    """
    Extended user profile for news platform.
    NOT tenant-scoped - users can belong to multiple companies.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='news_profile',
        primary_key=True
    )
    
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('author', 'Author'),
        ('subscriber', 'Subscriber'),
        ('premium_subscriber', 'Premium Subscriber'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_verified = models.BooleanField(default=False)
    
    social_links = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_profiles'
        verbose_name = _('News Profile')
        verbose_name_plural = _('News Profiles')
    
    def __str__(self):
        return f"{self.full_name or self.user.email} ({self.role})"


class Category(models.Model):
    """Article categories - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='news_categories',
        db_index=True
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    
    sort_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_categories'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        unique_together = [['company', 'slug']]
        indexes = [
            models.Index(fields=['company', 'slug']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Tag(models.Model):
    """Article tags - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='news_tags',
        db_index=True
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6B7280')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_tags'
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        unique_together = [['company', 'slug']]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Media(models.Model):
    """Media files - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='news_media',
        db_index=True
    )
    
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255, blank=True)
    file_path = models.CharField(max_length=500)
    file_url = models.URLField()
    file_size = models.IntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100)
    
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('embed', 'Embed'),
    ]
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_news_media'
    )
    is_public = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_media'
        verbose_name = _('Media')
        verbose_name_plural = _('Media')
        indexes = [
            models.Index(fields=['company', 'media_type']),
            models.Index(fields=['company', 'uploaded_by']),
        ]
    
    def __str__(self):
        return self.filename


class Gallery(models.Model):
    """Media galleries - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='news_galleries',
        db_index=True
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, db_index=True)
    cover_image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gallery_covers'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_galleries'
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')
        unique_together = [['company', 'slug']]
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"


class GalleryMedia(models.Model):
    """Gallery media relationships."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='gallery_items')
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_gallery_media'
        unique_together = [['gallery', 'media']]
    
    def __str__(self):
        return f"{self.gallery.title} - {self.media.filename}"


class Article(models.Model):
    """News articles - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='articles',
        db_index=True
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True)
    subtitle = models.CharField(max_length=300, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    
    CONTENT_TYPE_CHOICES = [
        ('article', 'Article'),
        ('gallery', 'Gallery'),
        ('video', 'Video'),
        ('podcast', 'Podcast'),
        ('live_blog', 'Live Blog'),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='article')
    
    featured_media = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_articles'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_articles'
    )
    co_authors = models.ManyToManyField(
        User,
        blank=True,
        related_name='co_authored_articles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('featured', 'Featured'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_premium = models.BooleanField(default=False)
    is_breaking_news = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    social_image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='social_articles'
    )
    
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    read_time_minutes = models.IntegerField(null=True, blank=True)
    
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    location_name = models.CharField(max_length=200, blank=True)
    
    version = models.IntegerField(default=1)
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'news_articles'
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        unique_together = [['company', 'slug']]
        indexes = [
            models.Index(fields=['company', 'status', 'published_at']),
            models.Index(fields=['company', 'author']),
            models.Index(fields=['company', 'category']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"


class ArticleMedia(models.Model):
    """Article media relationships."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_media_relations')
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_article_media'
        verbose_name = _('Article Media')
        verbose_name_plural = _('Article Media')
    
    def __str__(self):
        return f"{self.article.title} - {self.media.filename}"


class Comment(models.Model):
    """Article comments - scoped via article."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_comments'
    )
    author_name = models.CharField(max_length=200, blank=True)
    author_email = models.EmailField(blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_comments'
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        indexes = [
            models.Index(fields=['article', 'is_approved']),
        ]
    
    def __str__(self):
        return f"Comment on {self.article.title} by {self.author_name or self.author}"


class Business(models.Model):
    """Business directory listings - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='businesses',
        db_index=True
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    website_url = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    
    logo = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='business_logos'
    )
    cover_image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='business_covers'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_businesses'
    )
    
    business_hours = models.JSONField(default=dict, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    services = models.JSONField(default=list, blank=True)
    
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    review_count = models.IntegerField(default=0)
    
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_businesses'
        verbose_name = _('Business')
        verbose_name_plural = _('Businesses')
        unique_together = [['company', 'slug']]
        indexes = [
            models.Index(fields=['company', 'is_verified']),
            models.Index(fields=['company', 'industry']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class BusinessMedia(models.Model):
    """Business media relationships."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_media_relations')
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=20, blank=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_business_media'
        verbose_name = _('Business Media')
        verbose_name_plural = _('Business Media')
    
    def __str__(self):
        return f"{self.business.name} - {self.media.filename}"


class BusinessReview(models.Model):
    """Business reviews."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='business_reviews'
    )
    reviewer_name = models.CharField(max_length=200, blank=True)
    reviewer_email = models.EmailField(blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_business_reviews'
        verbose_name = _('Business Review')
        verbose_name_plural = _('Business Reviews')
    
    def __str__(self):
        return f"Review for {self.business.name} by {self.reviewer_name or self.reviewer}"


class Advertisement(models.Model):
    """Advertisements - scoped via business."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='advertisements')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='advertisements'
    )
    image_url = models.URLField(blank=True)
    link_url = models.URLField(blank=True)
    
    POSITION_CHOICES = [
        ('header', 'Header'),
        ('sidebar', 'Sidebar'),
        ('content', 'Content'),
        ('footer', 'Footer'),
    ]
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
        ('pending_approval', 'Pending Approval'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_advertisements'
        verbose_name = _('Advertisement')
        verbose_name_plural = _('Advertisements')
    
    def __str__(self):
        return f"{self.business.name} - {self.title}"


class RSSSource(models.Model):
    """RSS feed sources - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='rss_sources',
        db_index=True
    )
    
    name = models.CharField(max_length=200)
    url = models.URLField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    fetch_interval_minutes = models.IntegerField(default=60)
    max_articles_per_fetch = models.IntegerField(default=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_rss_sources'
        verbose_name = _('RSS Source')
        verbose_name_plural = _('RSS Sources')
        unique_together = [['company', 'url']]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class RSSArticleTracking(models.Model):
    """Track RSS articles to avoid duplicates."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rss_source = models.ForeignKey(RSSSource, on_delete=models.CASCADE, related_name='tracked_articles')
    external_id = models.CharField(max_length=500)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='rss_tracking')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_rss_article_tracking'
        verbose_name = _('RSS Article Tracking')
        verbose_name_plural = _('RSS Article Tracking')
        unique_together = [['rss_source', 'external_id']]
    
    def __str__(self):
        return f"{self.rss_source.name} - {self.external_id}"


class Notification(models.Model):
    """User notifications - with company context."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='news_notifications'
    )
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    
    TYPE_CHOICES = [
        ('breaking_news', 'Breaking News'),
        ('new_article', 'New Article'),
        ('comment_reply', 'Comment Reply'),
        ('subscription_reminder', 'Subscription Reminder'),
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_notifications'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['company', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class SiteSetting(models.Model):
    """Site settings - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='site_settings',
        db_index=True
    )
    
    key = models.CharField(max_length=100, db_index=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True)
    
    TYPE_CHOICES = [
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='string')
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_site_settings'
        verbose_name = _('Site Setting')
        verbose_name_plural = _('Site Settings')
        unique_together = [['company', 'key']]
    
    def __str__(self):
        return f"{self.company.name} - {self.key}"


class TeamMember(models.Model):
    """Team members - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='team_members',
        db_index=True
    )
    
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_member_images'
    )
    social_links = models.JSONField(default=dict, blank=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_team_members'
        verbose_name = _('Team Member')
        verbose_name_plural = _('Team Members')
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Testimonial(models.Model):
    """Testimonials - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='testimonials',
        db_index=True
    )
    
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonial_images'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_testimonials'
        verbose_name = _('Testimonial')
        verbose_name_plural = _('Testimonials')
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class AudioRecording(models.Model):
    """Audio recordings - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_recordings')
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='audio_recordings',
        db_index=True
    )
    media = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audio_recordings'
    )
    audio_url = models.URLField()
    transcription = models.TextField(blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_audio_recordings'
        verbose_name = _('Audio Recording')
        verbose_name_plural = _('Audio Recordings')
    
    def __str__(self):
        return f"{self.company.name} - {self.audio_url}"


class ContentImport(models.Model):
    """Content imports - scoped to company."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_imports')
    company = models.ForeignKey(
        'ecommerce.EcommerceCompany',
        on_delete=models.CASCADE,
        related_name='content_imports',
        db_index=True
    )
    filename = models.CharField(max_length=255)
    file_url = models.URLField()
    imported_articles = models.IntegerField(default=0)
    total_articles = models.IntegerField(default=0)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'news_content_imports'
        verbose_name = _('Content Import')
        verbose_name_plural = _('Content Imports')
    
    def __str__(self):
        return f"{self.company.name} - {self.filename}"


class UserSession(models.Model):
    """User sessions for analytics - NOT tenant-scoped."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_sessions'
    )
    session_id = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    page_views = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'news_user_sessions'
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
    
    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.session_id}"

