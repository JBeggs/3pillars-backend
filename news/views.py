"""
API viewsets for news platform.
All viewsets automatically filter by company from X-Company-Id header.
"""
import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Max
from django.utils import timezone

from .models import (
    Profile, Category, Tag, Media, Gallery, GalleryMedia,
    Article, ArticleMedia, Comment, Business, BusinessMedia,
    BusinessReview, Advertisement, RSSSource, RSSArticleTracking,
    Notification, SiteSetting, TeamMember, Testimonial,
    AudioRecording, ContentImport, UserSession
)
from .serializers import (
    ProfileSerializer, CategorySerializer, TagSerializer,
    MediaSerializer, GallerySerializer, GalleryMediaSerializer,
    ArticleListSerializer, ArticleDetailSerializer,
    CommentSerializer, BusinessListSerializer, BusinessDetailSerializer,
    BusinessReviewSerializer, AdvertisementSerializer,
    RSSSourceSerializer, NotificationSerializer, SiteSettingSerializer,
    TeamMemberSerializer, TestimonialSerializer
)
from .permissions import HasCompanyAccess, IsAuthorOrReadOnly, IsBusinessOwnerOrReadOnly
from .utils import get_company_from_request, filter_by_company

logger = logging.getLogger(__name__)


class CompanyScopedViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that automatically filters by company.
    All news platform viewsets should inherit from this.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, HasCompanyAccess]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        """Filter queryset by company from request."""
        queryset = super().get_queryset()
        company = get_company_from_request(self.request)
        
        if not company:
            # No company context = no data (unless superuser)
            if self.request.user.is_superuser:
                return queryset
            return queryset.none()
        
        # Filter by company
        if hasattr(queryset.model, 'company'):
            return queryset.filter(company=company)
        
        # For models without direct company FK, filter via related models
        return queryset
    
    def perform_create(self, serializer):
        """Automatically set company from request."""
        company = get_company_from_request(self.request)
        if not company:
            raise PermissionDenied('Company context required. Provide X-Company-Id header.')
        
        if hasattr(serializer.Meta.model, 'company'):
            serializer.save(company=company)
        else:
            serializer.save()


class CategoryViewSet(CompanyScopedViewSet):
    """ViewSet for Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'name']


class TagViewSet(CompanyScopedViewSet):
    """ViewSet for Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class MediaViewSet(CompanyScopedViewSet):
    """ViewSet for Media."""
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, HasCompanyAccess]
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['media_type', 'is_public']
    search_fields = ['filename', 'original_filename', 'alt_text', 'caption']
    ordering_fields = ['created_at', 'filename']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by company and handle public/private access."""
        queryset = super().get_queryset()
        company = get_company_from_request(self.request)
        
        if not company:
            if self.request.user.is_superuser:
                return queryset
            return queryset.none()
        
        # Filter by company
        queryset = queryset.filter(company=company)
        
        # If not authenticated, only show public media
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        # If authenticated, show public + own media
        elif not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(is_public=True) | Q(uploaded_by=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set company and uploaded_by."""
        company = get_company_from_request(self.request)
        if not company:
            raise PermissionDenied('Company context required.')
        
        serializer.save(
            company=company,
            uploaded_by=self.request.user if self.request.user.is_authenticated else None
        )


class GalleryViewSet(CompanyScopedViewSet):
    """ViewSet for Gallery."""
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    search_fields = ['title', 'description']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', '-created_at']
    
    def perform_create(self, serializer):
        """Set company and created_by."""
        company = get_company_from_request(self.request)
        serializer.save(
            company=company,
            created_by=self.request.user
        )


class ArticleViewSet(CompanyScopedViewSet):
    """ViewSet for Article."""
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, HasCompanyAccess, IsAuthorOrReadOnly]
    filterset_fields = ['status', 'category', 'is_premium', 'is_breaking_news', 'is_trending', 'slug', 'author']
    search_fields = ['title', 'subtitle', 'excerpt', 'content']
    ordering_fields = ['published_at', 'created_at', 'views', 'likes']
    ordering = ['-published_at', '-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail."""
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer
    
    def get_queryset(self):
        """Filter by company and handle published status."""
        from ecommerce.models import EcommerceCompany
        from django.db.models import Q
        # Don't call super().get_queryset() - it returns empty if no company header
        # Instead, get the base queryset directly
        queryset = Article.objects.all()
        company = get_company_from_request(self.request)
        
        # Always include Riverside Herald articles (the news platform company)
        # Articles belong to Riverside Herald, not individual business companies
        try:
            riverside_company = EcommerceCompany.objects.filter(
                Q(name__icontains='riverside') | Q(slug__icontains='riverside-herald') | Q(name__icontains='riverside herald')
            ).first()
            
            if riverside_company:
                # Filter by Riverside Herald company - this is where articles belong
                queryset = queryset.filter(company=riverside_company)
            elif company:
                # Fallback: if Riverside Herald not found, use the company from header
                queryset = queryset.filter(company=company)
            # If no company found, don't filter - show all articles
            # This ensures articles are always visible
        except Exception as e:
            logger.error(f"Error filtering articles by company: {e}", exc_info=True)
            # Fallback: if error, try to use company from header
            if company:
                queryset = queryset.filter(company=company)
            # If no company, don't filter - show all articles
        
        # Filter by status based on user permissions
        if not self.request.user.is_authenticated:
            # Anonymous: only published articles
            queryset = queryset.filter(status='published')
        else:
            # Authenticated users: published articles + their own drafts (or all drafts if admin/editor)
            # Check user profile role
            is_admin_or_editor = False
            is_author_or_business_owner = False
            if hasattr(self.request.user, 'news_profile'):
                profile = self.request.user.news_profile
                is_admin_or_editor = profile.role in ['admin', 'editor']
                is_author_or_business_owner = profile.role in ['author', 'business_owner']
            
            if is_admin_or_editor:
                # Admins and editors can see all articles (published and drafts)
                pass  # No status filtering - they see everything
            elif is_author_or_business_owner:
                # Authors and business owners can see published articles + their own drafts only
                # BUT: Business owners should ONLY see their own articles (not all published articles)
                if profile.role == 'business_owner':
                    # Business owners: only their own articles (published + drafts)
                    queryset = queryset.filter(author=self.request.user)
                else:
                    # Authors: published articles + their own drafts
                    queryset = queryset.filter(
                        Q(status='published') | 
                        Q(status='draft', author=self.request.user)
                    )
            else:
                # Other authenticated users (regular users) see only published articles
                queryset = queryset.filter(status='published')
        
        return queryset
    
    def perform_create(self, serializer):
        """Set company and author."""
        from ecommerce.models import EcommerceCompany
        from django.db.models import Q
        
        company = get_company_from_request(self.request)
        
        # Articles always belong to Riverside Herald (the news platform company)
        # Even if business owner's company is in header, use Riverside Herald
        try:
            riverside_company = EcommerceCompany.objects.filter(
                Q(name__icontains='riverside') | Q(slug__icontains='riverside-herald') | Q(name__icontains='riverside herald')
            ).first()
            if riverside_company:
                company = riverside_company
        except Exception as e:
            logger.error(f"Error finding Riverside Herald company: {e}", exc_info=True)
        
        # If still no company, raise error
        if not company:
            raise PermissionDenied('Riverside Herald company not found. Articles must belong to the news platform company.')
        
        serializer.save(
            company=company,
            author=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Increment article views."""
        article = self.get_object()
        article.views += 1
        article.save(update_fields=['views'])
        return Response({'views': article.views})
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like an article."""
        article = self.get_object()
        article.likes += 1
        article.save(update_fields=['likes'])
        return Response({'likes': article.likes})
    
    @action(detail=True, methods=['get', 'post', 'delete'], url_path='media')
    def manage_media(self, request, pk=None):
        """Manage article media gallery."""
        article = self.get_object()
        company = get_company_from_request(request)
        
        # Check permissions - user must be author, editor, admin, or company owner
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has permission to modify this article
        has_permission = False
        if article.author == request.user:
            has_permission = True
        elif hasattr(request.user, 'news_profile'):
            profile = request.user.news_profile
            if profile.role in ['admin', 'editor']:
                has_permission = True
        if company and company.owner == request.user:
            has_permission = True
        if request.user.is_superuser:
            has_permission = True
        
        if request.method == 'GET':
            # GET is allowed for authenticated users (read-only)
            media_relations = article.article_media_relations.all().order_by('sort_order')
            from .serializers import ArticleMediaSerializer
            serializer = ArticleMediaSerializer(media_relations, many=True, context={'request': request})
            return Response(serializer.data)
        
        # POST and DELETE require write permissions
        if not has_permission:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        elif request.method == 'POST':
            # Add media to article
            media_id = request.data.get('media_id')
            if not media_id:
                return Response({'error': 'media_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert to string if needed (UUID handling)
            if not isinstance(media_id, str):
                media_id = str(media_id)
            
            try:
                media = Media.objects.get(id=media_id, company=company)
            except Media.DoesNotExist:
                return Response({
                    'error': 'Media not found',
                    'details': f'Media with id {media_id} not found for company {company.id if company else "unknown"}'
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({
                    'error': 'Error fetching media',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Check if media is already in article (prevent duplicates)
            existing = article.article_media_relations.filter(media_id=media_id).first()
            if existing:
                # Update existing entry if caption provided
                if request.data.get('caption'):
                    existing.caption = request.data.get('caption')
                    existing.save()
                from .serializers import ArticleMediaSerializer
                serializer = ArticleMediaSerializer(existing, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # Get max sort_order for this article
            max_order = article.article_media_relations.aggregate(
                max_order=Max('sort_order')
            )['max_order'] or 0
            
            article_media = ArticleMedia.objects.create(
                article=article,
                media=media,
                sort_order=max_order + 1,
                caption=request.data.get('caption', '')
            )
            
            from .serializers import ArticleMediaSerializer
            serializer = ArticleMediaSerializer(article_media, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            # Remove media from article
            media_id = request.data.get('media_id')
            if not media_id:
                return Response({'error': 'media_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert to string if needed (UUID handling)
            if not isinstance(media_id, str):
                media_id = str(media_id)
            
            try:
                article_media = article.article_media_relations.get(media_id=media_id)
                article_media.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ArticleMedia.DoesNotExist:
                return Response({
                    'error': 'Media not found in article',
                    'details': f'Media with id {media_id} not found in article {article.id}'
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({
                    'error': 'Error removing media',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['article', 'is_approved']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by article's company."""
        queryset = super().get_queryset()
        company = get_company_from_request(self.request)
        
        if not company:
            if self.request.user.is_superuser:
                return queryset
            return queryset.none()
        
        # Filter comments for articles in this company
        queryset = queryset.filter(article__company=company)
        
        # Only show approved comments to non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_approved=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set author if authenticated."""
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            serializer.save()


class BusinessViewSet(CompanyScopedViewSet):
    """ViewSet for Business."""
    queryset = Business.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, HasCompanyAccess, IsBusinessOwnerOrReadOnly]
    filterset_fields = ['industry', 'is_verified', 'owner']
    search_fields = ['name', 'description', 'industry', 'city', 'state']
    ordering_fields = ['name', 'rating', 'review_count', 'created_at']
    ordering = ['-is_verified', '-rating', 'name']
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail."""
        if self.action == 'list':
            return BusinessListSerializer
        return BusinessDetailSerializer
    
    def get_queryset(self):
        """Filter by company, but allow business owners to see their own businesses.
        For public/homepage access, show businesses from Riverside Herald company."""
        from ecommerce.models import EcommerceCompany
        # Don't call super().get_queryset() - it returns empty if no company header
        # Instead, get the base queryset directly
        queryset = Business.objects.all()
        company = get_company_from_request(self.request)
        
        # Try to find Riverside Herald company for public display
        try:
            riverside_company = EcommerceCompany.objects.filter(
                Q(name__icontains='riverside') | Q(slug__icontains='riverside-herald') | Q(name__icontains='riverside herald')
            ).first()
        except Exception:
            riverside_company = None
        
        if not company:
            if self.request.user.is_superuser:
                return queryset
            # If no company context but user is authenticated, show their own businesses
            if self.request.user.is_authenticated:
                return queryset.filter(owner=self.request.user)
            # For anonymous users (homepage), show businesses from Riverside Herald
            if riverside_company:
                return queryset.filter(company=riverside_company)
            # If no Riverside Herald found, return empty (better than showing all businesses)
            return queryset.none()
        
        # Filter by company OR businesses owned by this user
        # This allows business owners to see and edit their own businesses even if viewing from different company
        if self.request.user.is_authenticated:
            # Always include businesses owned by the user, regardless of company header
            # Also include businesses from the company in header (if provided)
            queryset = queryset.filter(
                Q(company=company) | Q(owner=self.request.user)
            )
        else:
            # For anonymous users, show businesses from the company in header
            # But also include Riverside Herald businesses for homepage
            if riverside_company and company != riverside_company:
                queryset = queryset.filter(
                    Q(company=company) | Q(company=riverside_company)
                )
            else:
                queryset = queryset.filter(company=company)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set company and owner. Businesses belong to Riverside Herald company."""
        from ecommerce.models import EcommerceCompany
        from django.db.models import Q
        
        # Businesses always belong to Riverside Herald (the news platform company)
        # Find Riverside Herald company
        riverside_company = None
        try:
            riverside_company = EcommerceCompany.objects.filter(
                Q(name__icontains='riverside') | Q(slug__icontains='riverside-herald') | Q(name__icontains='riverside herald')
            ).first()
        except Exception as e:
            logger.error(f"Error finding Riverside Herald company: {e}", exc_info=True)
        
        if not riverside_company:
            raise PermissionDenied('Riverside Herald company not found. Businesses must belong to the news platform company.')
        
        # Auto-generate slug if not provided
        if not serializer.validated_data.get('slug') and serializer.validated_data.get('name'):
            from django.utils.text import slugify
            base_slug = slugify(serializer.validated_data['name'])
            slug = base_slug
            counter = 1
            # Ensure unique slug within company
            while Business.objects.filter(company=riverside_company, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            serializer.validated_data['slug'] = slug
        
        serializer.save(
            company=riverside_company,  # Always use Riverside Herald
            owner=self.request.user
        )


class BusinessReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Business Review."""
    queryset = BusinessReview.objects.all()
    serializer_class = BusinessReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['business', 'is_approved', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by business's company."""
        queryset = super().get_queryset()
        company = get_company_from_request(self.request)
        
        if not company:
            if self.request.user.is_superuser:
                return queryset
            return queryset.none()
        
        # Filter reviews for businesses in this company
        queryset = queryset.filter(business__company=company)
        
        # Only show approved reviews to non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_approved=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set reviewer if authenticated."""
        if self.request.user.is_authenticated:
            serializer.save(reviewer=self.request.user)
        else:
            serializer.save()


class AdvertisementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Advertisement (read-only for public)."""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['position', 'status', 'business']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by business's company and status."""
        queryset = super().get_queryset()
        company = get_company_from_request(self.request)
        
        if not company:
            if self.request.user.is_superuser:
                return queryset
            return queryset.none()
        
        # Filter ads for businesses in this company
        queryset = queryset.filter(business__company=company)
        
        # Only show active ads to non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='active')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def increment_impression(self, request, pk=None):
        """Increment ad impression."""
        ad = self.get_object()
        ad.impressions += 1
        ad.save(update_fields=['impressions'])
        return Response({'impressions': ad.impressions})
    
    @action(detail=True, methods=['post'])
    def increment_click(self, request, pk=None):
        """Increment ad click."""
        ad = self.get_object()
        ad.clicks += 1
        ad.save(update_fields=['clicks'])
        return Response({'clicks': ad.clicks})


class RSSSourceViewSet(CompanyScopedViewSet):
    """ViewSet for RSS Source."""
    queryset = RSSSource.objects.all()
    serializer_class = RSSSourceSerializer
    permission_classes = [IsAuthenticated, HasCompanyAccess]
    filterset_fields = ['status', 'category']
    search_fields = ['name', 'url']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Notification (read-only, user's own notifications)."""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['type', 'is_read', 'company']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Only show user's own notifications."""
        return Notification.objects.filter(user=self.request.user)


class SiteSettingViewSet(viewsets.ModelViewSet):
    """ViewSet for Site Setting."""
    queryset = SiteSetting.objects.all()
    serializer_class = SiteSettingSerializer
    # Allow public read access, require auth for write
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['key', 'description']
    ordering_fields = ['key']
    ordering = ['key']
    
    def get_queryset(self):
        """Filter by company and public visibility."""
        try:
            queryset = super().get_queryset()
            company = get_company_from_request(self.request)
            
            if not company:
                # If no company ID provided, return empty (unless superuser)
                if self.request.user.is_superuser:
                    return queryset
                return queryset.none()
            
            queryset = queryset.filter(company=company)
            
            # Non-authenticated users only see public settings
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(is_public=True)
            
            return queryset
        except Exception as e:
            logger.error(f"Error in SiteSettingViewSet.get_queryset: {e}", exc_info=True)
            # Return empty queryset on error to prevent 500
            return SiteSetting.objects.none()
    
    def perform_create(self, serializer):
        """Require company access for creating settings."""
        company = get_company_from_request(self.request)
        if not company:
            raise PermissionDenied('Company context required. Provide X-Company-Id header.')
        
        # Check company access for write operations
        if not (company.owner == self.request.user or 
                (hasattr(company, 'users') and self.request.user in company.users.all()) or
                self.request.user.is_superuser):
            raise PermissionDenied('You do not have access to this company.')
        
        serializer.save(company=company)
    
    def perform_update(self, serializer):
        """Require company access for updating settings."""
        company = get_company_from_request(self.request)
        if not company:
            raise PermissionDenied('Company context required. Provide X-Company-Id header.')
        
        # Check company access for write operations
        if not (company.owner == self.request.user or 
                (hasattr(company, 'users') and self.request.user in company.users.all()) or
                self.request.user.is_superuser):
            raise PermissionDenied('You do not have access to this company.')
        
        serializer.save()


class TeamMemberViewSet(CompanyScopedViewSet):
    """ViewSet for Team Member."""
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    filterset_fields = ['is_featured']
    search_fields = ['name', 'title', 'bio']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'name']


class TestimonialViewSet(CompanyScopedViewSet):
    """ViewSet for Testimonial."""
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    filterset_fields = ['is_featured', 'rating']
    search_fields = ['name', 'title', 'company_name', 'content']
    ordering_fields = ['sort_order', 'created_at', 'rating']
    ordering = ['sort_order', '-created_at']


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Profile (user's own profile)."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show user's own profile."""
        return Profile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user's profile."""
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = Profile.objects.create(user=request.user)
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class StatsViewSet(viewsets.ViewSet):
    """ViewSet for system statistics (admin/editor only)."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'error': 'Company context required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user has admin/editor role
        if hasattr(request.user, 'news_profile'):
            profile = request.user.news_profile
            if profile.role not in ['admin', 'editor']:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get stats for this company
        stats = {
            'total_articles': Article.objects.filter(company=company).count(),
            'published_articles': Article.objects.filter(company=company, status='published').count(),
            'draft_articles': Article.objects.filter(company=company, status='draft').count(),
            'scheduled_articles': Article.objects.filter(company=company, status='scheduled').count(),
            'total_users': Profile.objects.count(),  # All users (not tenant-scoped)
            'total_businesses': Business.objects.filter(company=company).count(),
            'total_categories': Category.objects.filter(company=company).count(),
            'total_tags': Tag.objects.filter(company=company).count(),
        }
        
        # Get user's articles if author or business owner
        if profile.role in ['author', 'business_owner']:
            stats['my_articles'] = Article.objects.filter(
                company=company,
                author=request.user
            ).count()
        
        return Response(stats)

