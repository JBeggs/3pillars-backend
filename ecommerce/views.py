"""
API viewsets for e-commerce multi-tenant product management.
Based on JavaMellow Backend API Specification.
"""
import logging
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from .models import EcommerceCompany, EcommerceProduct, Category, ProductImage, CompanyIntegrationSettings
from .serializers import (
    EcommerceCompanySerializer,
    EcommerceProductSerializer,
    CategorySerializer,
    ProductImageSerializer,
    BulkOperationSerializer,
    CompanyIntegrationSettingsSerializer,
)
from .permissions import IsCompanyOwnerOrReadOnly, IsCompanyMember
from .utils import get_company_from_request, filter_by_company

logger = logging.getLogger(__name__)


class EcommerceCompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for E-commerce Company management.
    """
    queryset = EcommerceCompany.objects.all()
    serializer_class = EcommerceCompanySerializer
    permission_classes = [IsAuthenticated, IsCompanyOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'plan']
    search_fields = ['name', 'email', 'slug']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter companies by user access."""
        user = self.request.user
        queryset = EcommerceCompany.objects.all()
        
        # Superusers can see all companies
        if user.is_superuser:
            return queryset
        
        # Regular users can only see their own company
        return queryset.filter(owner=user)
    
    def perform_create(self, serializer):
        """Set owner to current user when creating company."""
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's company."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'No company found for user'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(company)
        return Response({'success': True, 'data': serializer.data})


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category management (company-scoped).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'slug']
    
    def get_queryset(self):
        """Filter categories by company."""
        company = get_company_from_request(self.request)
        queryset = Category.objects.all()
        return filter_by_company(queryset, company)
    
    def perform_create(self, serializer):
        """Set company from request."""
        company = get_company_from_request(self.request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(company=company)


class EcommerceProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for E-commerce Product management (company-scoped).
    Implements all endpoints from JavaMellow API specification.
    """
    queryset = EcommerceProduct.objects.all()
    serializer_class = EcommerceProductSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'featured', 'in_stock']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']
    ordering = ['-created_at']
    lookup_field = 'id'
    
    def get_queryset(self):
        """Filter products by company with advanced filtering."""
        company = get_company_from_request(self.request)
        queryset = EcommerceProduct.objects.all()
        queryset = filter_by_company(queryset, company)
        
        # Additional filters from query params
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        featured = self.request.query_params.get('featured')
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == 'true')
        
        in_stock = self.request.query_params.get('inStock')
        if in_stock is not None:
            queryset = queryset.filter(in_stock=in_stock.lower() == 'true')
        
        # Tag filtering
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__overlap=tag_list)
        
        # Price range filtering
        min_price = self.request.query_params.get('minPrice')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        max_price = self.request.query_params.get('maxPrice')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Low stock filtering
        low_stock = self.request.query_params.get('lowStock')
        if low_stock == 'true':
            threshold = int(self.request.query_params.get('threshold', 10))
            queryset = queryset.filter(
                track_inventory=True,
                stock_quantity__lte=threshold,
                in_stock=True
            )
        
        return queryset.select_related('company', 'category')
    
    def get_serializer_context(self):
        """Add company to serializer context."""
        context = super().get_serializer_context()
        context['company'] = get_company_from_request(self.request)
        return context
    
    def perform_create(self, serializer):
        """Set company from request and auto-generate slug if needed."""
        company = get_company_from_request(self.request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Auto-generate slug from name if not provided
        if 'slug' not in serializer.validated_data or not serializer.validated_data['slug']:
            from django.utils.text import slugify
            name = serializer.validated_data['name']
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while EcommerceProduct.objects.filter(company=company, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            serializer.validated_data['slug'] = slug
        
        serializer.save(company=company)
    
    @action(detail=False, methods=['get'], url_path='slug/(?P<slug>[^/.]+)')
    def get_by_slug(self, request, slug=None):
        """Get product by slug (company-scoped)."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = EcommerceProduct.objects.get(company=company, slug=slug)
            serializer = self.get_serializer(product)
            return Response({'success': True, 'data': serializer.data})
        except EcommerceProduct.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 'PRODUCT_NOT_FOUND', 'message': f'Product with slug "{slug}" not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """Bulk operations on products."""
        serializer = BulkOperationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid request', 'details': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        operation = serializer.validated_data['operation']
        ids = serializer.validated_data['ids']
        data = serializer.validated_data.get('data', {})
        
        # Filter products by company
        products = EcommerceProduct.objects.filter(id__in=ids, company=company)
        
        updated = 0
        failed = 0
        
        if operation == 'update':
            products.update(**data)
            updated = products.count()
        elif operation == 'delete':
            updated = products.delete()[0]
        elif operation == 'archive':
            products.update(status='archived')
            updated = products.count()
        
        return Response({
            'success': True,
            'message': 'Bulk operation completed',
            'updated': updated,
            'failed': failed
        })
    
    @action(detail=True, methods=['put'], url_path='stock')
    def update_stock(self, request, id=None):
        """Update product stock."""
        product = self.get_object()
        stock_quantity = request.data.get('stockQuantity')
        in_stock = request.data.get('inStock')
        
        if stock_quantity is not None:
            product.stock_quantity = stock_quantity
        if in_stock is not None:
            product.in_stock = in_stock
        
        product.save()
        serializer = self.get_serializer(product)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['get'], url_path='autocomplete')
    def autocomplete(self, request):
        """Product autocomplete for search."""
        company = get_company_from_request(request)
        if not company:
            return Response({'success': True, 'data': []})
        
        q = request.query_params.get('q', '')
        if not q:
            return Response({'success': True, 'data': []})
        
        products = EcommerceProduct.objects.filter(
            company=company,
            status='active'
        ).filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )[:10]
        
        data = [{
            'id': str(p.id),
            'name': p.name,
            'slug': p.slug,
            'image': p.image,
        } for p in products]
        
        return Response({'success': True, 'data': data})
    
    def list(self, request, *args, **kwargs):
        """Override list to return paginated response with success wrapper."""
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': response.data.get('results', []),
            'pagination': {
                'page': response.data.get('page', 1),
                'limit': response.data.get('page_size', 20),
                'total': response.data.get('count', 0),
                'totalPages': (response.data.get('count', 0) + response.data.get('page_size', 20) - 1) // response.data.get('page_size', 20),
                'hasNext': response.data.get('next') is not None,
                'hasPrev': response.data.get('previous') is not None,
            }
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return success wrapper."""
        response = super().retrieve(request, *args, **kwargs)
        return Response({'success': True, 'data': response.data})
    
    def create(self, request, *args, **kwargs):
        """Override create to return success wrapper and handle errors."""
        try:
            response = super().create(request, *args, **kwargs)
            return Response({'success': True, 'data': response.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating product: {str(e)}', exc_info=True)
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Override update to return success wrapper."""
        try:
            response = super().update(request, *args, **kwargs)
            return Response({'success': True, 'data': response.data})
        except Exception as e:
            logger.error(f'Error updating product: {str(e)}', exc_info=True)
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to return success wrapper."""
        super().destroy(request, *args, **kwargs)
        return Response({'success': True, 'message': 'Product deleted successfully'})


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product Image management.
    """
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter images by company."""
        company = get_company_from_request(self.request)
        queryset = ProductImage.objects.all()
        return filter_by_company(queryset, company)
    
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """Upload a single product image."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'file' not in request.FILES:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'No file provided'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/svg+xml']
        if file.content_type not in allowed_types:
            return Response(
                {'success': False, 'error': {'code': 'INVALID_IMAGE_FORMAT', 'message': f'Invalid image format. Allowed: {", ".join(allowed_types)}'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (5MB max)
        if file.size > 5 * 1024 * 1024:
            return Response(
                {'success': False, 'error': {'code': 'FILE_TOO_LARGE', 'message': 'File size exceeds 5MB limit'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save file to local storage
        from django.conf import settings
        from pathlib import Path
        import uuid
        
        # Create directory structure: media/companies/{company_id}/products/
        company_media_dir = Path(settings.MEDIA_ROOT) / 'companies' / str(company.id) / 'products'
        company_media_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_ext = Path(file.name).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = company_media_dir / unique_filename
        
        # Save file
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Get image dimensions if possible
        width = None
        height = None
        try:
            from PIL import Image
            img = Image.open(file_path)
            width, height = img.size
        except ImportError:
            pass  # PIL not available
        except Exception:
            pass  # Couldn't read image dimensions
        
        # Build URLs - use request to get absolute URL
        request_host = request.get_host() if hasattr(request, 'get_host') else None
        if request_host and not request_host.startswith('http'):
            scheme = 'https' if request.is_secure() else 'http'
            base_url = f"{scheme}://{request_host}"
        else:
            base_url = ''
        
        media_url = settings.MEDIA_URL.rstrip('/')
        relative_path = f"companies/{company.id}/products/{unique_filename}"
        
        if base_url:
            image_url = f"{base_url}{media_url}/{relative_path}"
        else:
            image_url = f"{media_url}/{relative_path}"
        
        image_data = {
            'url': image_url,
            'thumbnail_url': image_url,  # Same URL for now, can add thumbnail generation later
            'filename': file.name,
            'size': file.size,
            'width': width,
            'height': height,
            'mime_type': file.content_type,
        }
        
        # Create ProductImage record
        product_image = ProductImage.objects.create(
            company=company,
            url=image_data['url'],
            thumbnail_url=image_data['thumbnail_url'],
            filename=file.name,
            size=image_data['size'],
            width=image_data['width'],
            height=image_data['height'],
            mime_type=image_data['mime_type'],
        )
        
        serializer = self.get_serializer(product_image)
        return Response({'success': True, 'data': serializer.data})
    
    @action(detail=False, methods=['post'], url_path='upload-multiple')
    def upload_multiple(self, request):
        """Upload multiple product images."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        files = request.FILES.getlist('files[]')
        if not files:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'No files provided'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_images = []
        errors = []
        
        for file in files:
            try:
                # Validate file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/svg+xml']
                if file.content_type not in allowed_types:
                    errors.append(f'{file.name}: Invalid image format')
                    continue
                
                # Validate file size
                if file.size > 5 * 1024 * 1024:
                    errors.append(f'{file.name}: File size exceeds 5MB')
                    continue
                
                # Save file to local storage
                from django.conf import settings
                from pathlib import Path
                import uuid
                
                # Create directory structure: media/companies/{company_id}/products/
                company_media_dir = Path(settings.MEDIA_ROOT) / 'companies' / str(company.id) / 'products'
                company_media_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate unique filename
                file_ext = Path(file.name).suffix
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                file_path = company_media_dir / unique_filename
                
                # Save file
                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                # Get image dimensions if possible
                width = None
                height = None
                try:
                    from PIL import Image
                    img = Image.open(file_path)
                    width, height = img.size
                except ImportError:
                    pass
                except Exception:
                    pass
                
                # Build URLs - use request to get absolute URL
                request_host = request.get_host() if hasattr(request, 'get_host') else None
                if request_host and not request_host.startswith('http'):
                    scheme = 'https' if request.is_secure() else 'http'
                    base_url = f"{scheme}://{request_host}"
                else:
                    base_url = ''
                
                media_url = settings.MEDIA_URL.rstrip('/')
                relative_path = f"companies/{company.id}/products/{unique_filename}"
                
                if base_url:
                    image_url = f"{base_url}{media_url}/{relative_path}"
                else:
                    image_url = f"{media_url}/{relative_path}"
                
                product_image = ProductImage.objects.create(
                    company=company,
                    url=image_url,
                    thumbnail_url=image_url,
                    filename=file.name,
                    size=file.size,
                    width=width,
                    height=height,
                    mime_type=file.content_type,
                )
                
                serializer = self.get_serializer(product_image)
                uploaded_images.append(serializer.data)
            except Exception as e:
                errors.append(f'{file.name}: {str(e)}')
        
        return Response({
            'success': True,
            'data': uploaded_images,
            'errors': errors if errors else None
        })


class CompanyIntegrationSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Company Integration Settings (company-scoped, owner-only).
    """
    queryset = CompanyIntegrationSettings.objects.all()
    serializer_class = CompanyIntegrationSettingsSerializer
    permission_classes = [IsAuthenticated, IsCompanyOwnerOrReadOnly]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Filter settings by company."""
        company = get_company_from_request(self.request)
        if not company:
            return CompanyIntegrationSettings.objects.none()
        return CompanyIntegrationSettings.objects.filter(company=company)
    
    def get_object(self):
        """Get or create integration settings for company."""
        company = get_company_from_request(self.request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        settings, created = CompanyIntegrationSettings.objects.get_or_create(company=company)
        return settings
    
    def perform_create(self, serializer):
        """Set company from request."""
        company = get_company_from_request(self.request)
        if not company:
            raise serializers.ValidationError({'company': 'Company not found'})
        serializer.save(company=company)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current company's integration settings."""
        company = get_company_from_request(request)
        if not company:
            return Response(
                {'success': False, 'error': {'code': 'COMPANY_NOT_FOUND', 'message': 'Company not found'}},
                status=status.HTTP_404_NOT_FOUND
            )
        
        settings, created = CompanyIntegrationSettings.objects.get_or_create(company=company)
        serializer = self.get_serializer(settings)
        return Response({'success': True, 'data': serializer.data})

