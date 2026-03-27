from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.http import Http404
from django.contrib import messages

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .models import Article, Category, Rating
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    CategorySerializer,
    RatingSerializer,
)


ARTICLES_PER_PAGE = 12
CACHE_TIMEOUT = 60 * 5

def home_view(request):

    from django.db.models import Count, Avg

    def article_qs():
        """Annotate bilan optimallashtirilgan queryset"""
        return (
            Article.objects
            .filter(status='published')
            .select_related('author', 'category')
            .annotate(
                comments_count=Count('comments', filter=Q(comments__is_approved=True)),
                avg_rating=Avg('ratings__score'),
            )
        )

    featured = (
        article_qs()
        .filter(is_featured=True)
        .order_by('-published_at')[:3]
    )

    latest = (
        article_qs()
        .order_by('-published_at')[:12]
    )

    popular = (
        article_qs()
        .order_by('-views_count')[:5]
    )

    tutorials = (
        article_qs()
        .filter(content_type__in=['tutorial', 'video', 'course'])
        .order_by('-published_at')[:6]
    )

    categories = Category.objects.all()

    total_articles = Article.objects.filter(status='published').count()
    total_authors  = Article.objects.filter(status='published').values('author').distinct().count()

    return render(request, 'articles/home.html', {
        'featured':       featured,
        'latest':         latest,
        'popular':        popular,
        'tutorials':      tutorials,
        'categories':     categories,
        'total_articles': total_articles,
        'total_authors':  total_authors,
    })

# views.py ga qo'shimchalar
# Tepaga import qo'shing:
# from django.db.models import Count, Avg, Q, F

def article_list_view(request):
    """Maqolalar ro'yxati — filter, qidiruv, saralash, pagination"""
    from django.db.models import Count, Avg

    # Barcha maqolalar — annotate bilan (N+1 yo'q)
    queryset = (
        Article.objects
        .filter(status='published')
        .select_related('author', 'category')
        .annotate(
            comments_count=Count('comments', filter=Q(comments__is_approved=True)),
            avg_rating=Avg('ratings__score'),
        )
    )

    # Filterlar
    category_slug = request.GET.get('category', '').strip()
    content_type  = request.GET.get('type', '').strip()
    search        = request.GET.get('q', '').strip()
    sort          = request.GET.get('sort', 'newest').strip()

    ALLOWED_SORTS = {
        'newest':  '-published_at',
        'oldest':  'published_at',
        'popular': '-views_count',
    }
    sort_field = ALLOWED_SORTS.get(sort, '-published_at')

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    if content_type:
        queryset = queryset.filter(content_type=content_type)
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(tags__icontains=search)
        )

    queryset = queryset.order_by(sort_field)

    # Kategoriyalar — har birining maqola soni bilan
    categories = (
        Category.objects
        .annotate(article_count=Count('articles', filter=Q(articles__status='published')))
        .order_by('name')
    )

    active_category = categories.filter(slug=category_slug).first() if category_slug else None

    # Pagination
    paginator = Paginator(queryset, ARTICLES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    try:
        articles = paginator.page(page_number)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    return render(request, 'articles/list.html', {
        'articles':        articles,
        'categories':      categories,
        'active_category': active_category,
        'content_type':    content_type,
        'search':          search,
        'sort':            sort,
        'total_count':     paginator.count,
    })


def article_detail_view(request, slug):
    """Maqola tafsiloti"""
    article = get_object_or_404(
        Article.objects.select_related('author', 'category'),
        slug=slug,
        status='published',
    )

    # Ko'rishlar sonini oshirish — race condition xavfsiz
    Article.objects.filter(pk=article.pk).update(views_count=F('views_count') + 1)
    article.views_count = article.views_count + 1  # refresh_from_db() ni tejash

    comments = (
        article.comments
        .filter(is_approved=True)
        .select_related('author')
        .order_by('created_at')
    )

    related = (
        Article.objects
        .filter(status='published', category=article.category)
        .exclude(pk=article.pk)
        .select_related('author', 'category')
        .order_by('-published_at')[:4]
    )

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(
            article=article, user=request.user
        ).first()

    return render(request, 'articles/detail.html', {
        'article':        article,
        'comments':       comments,
        'related':        related,
        'user_rating':    user_rating,
        'average_rating': article.get_average_rating(),
        'rating_count':   article.get_rating_count(),
    })


def category_detail_view(request, slug):
    """Kategoriya sahifasi"""
    category = get_object_or_404(Category, slug=slug)
    queryset = (
        Article.objects
        .filter(status='published', category=category)
        .select_related('author', 'category')
        .order_by('-published_at')
    )

    paginator = Paginator(queryset, ARTICLES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    try:
        articles = paginator.page(page_number)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    categories = Category.objects.all()

    return render(request, 'articles/category.html', {
        'category':    category,
        'articles':    articles,
        'categories':  categories,
        'total_count': paginator.count,
    })


# ═════════════════════════════════════════════
# REST API Views
# ═════════════════════════════════════════════

class CategoryListAPIView(generics.ListAPIView):
    queryset            = Category.objects.all()
    serializer_class    = CategorySerializer
    permission_classes  = [permissions.AllowAny]
    throttle_classes    = [AnonRateThrottle]


class ArticleListAPIView(generics.ListAPIView):
    serializer_class   = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [AnonRateThrottle]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'content', 'tags']
    ordering_fields    = ['published_at', 'views_count', 'created_at']
    ordering           = ['-published_at']

    def get_queryset(self):
        qs = (
            Article.objects
            .filter(status='published')
            .select_related('author', 'category')
        )
        category     = self.request.query_params.get('category', '').strip()
        content_type = self.request.query_params.get('type', '').strip()

        if category:
            qs = qs.filter(category__slug=category)
        if content_type:
            qs = qs.filter(content_type=content_type)
        return qs


class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset           = Article.objects.filter(status='published').select_related('author', 'category')
    serializer_class   = ArticleDetailSerializer
    lookup_field       = 'slug'
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [AnonRateThrottle]


class RateArticleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes   = [UserRateThrottle]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug, status='published')

        serializer = RatingSerializer(
            data=request.data,
            context={'request': request, 'article': article},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            'average_rating': article.get_average_rating(),
            'rating_count':   article.get_rating_count(),
            'user_rating':    serializer.data['score'],
        }, status=status.HTTP_200_OK)