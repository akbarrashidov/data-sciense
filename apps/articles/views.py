from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .models import Article, Category, Rating
from .forms import ArticleRequestForm, ArticleForm
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    CategorySerializer,
    RatingSerializer,
)


# ─────────────────────────────────────────────
# Yordamchi konstantalar
# ─────────────────────────────────────────────
ARTICLES_PER_PAGE = 12
CACHE_TIMEOUT = 60 * 5  # 5 daqiqa


# ═════════════════════════════════════════════
# Template Views
# ═════════════════════════════════════════════

def home_view(request):
    """Bosh sahifa"""
    cache_key = 'home_page_data'
    ctx = cache.get(cache_key)

    if ctx is None:
        featured = (
            Article.objects
            .filter(status='published', is_featured=True)
            .select_related('author', 'category')
            .order_by('-published_at')[:3]
        )
        latest = (
            Article.objects
            .filter(status='published')
            .select_related('author', 'category')
            .order_by('-published_at')[:12]
        )
        categories = Category.objects.all()
        tutorials = (
            Article.objects
            .filter(status='published', content_type__in=['tutorial', 'video', 'course'])
            .select_related('author', 'category')
            .order_by('-published_at')[:6]
        )
        ctx = {
            'featured': list(featured),
            'latest': list(latest),
            'categories': list(categories),
            'tutorials': list(tutorials),
        }
        cache.set(cache_key, ctx, CACHE_TIMEOUT)

    return render(request, 'articles/home.html', ctx)


def article_list_view(request):
    """Maqolalar ro'yxati — filter, qidiruv, pagination"""
    queryset = (
        Article.objects
        .filter(status='published')
        .select_related('author', 'category')
        .order_by('-published_at')
    )

    # Filterlar
    category_slug = request.GET.get('category', '').strip()
    content_type  = request.GET.get('type', '').strip()
    search        = request.GET.get('q', '').strip()
    sort          = request.GET.get('sort', '-published_at')

    ALLOWED_SORTS = {
        'newest':   '-published_at',
        'oldest':   'published_at',
        'popular':  '-views_count',
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

    # Pagination
    paginator = Paginator(queryset, ARTICLES_PER_PAGE)
    page_number = request.GET.get('page', 1)
    try:
        articles = paginator.page(page_number)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    categories = (
        Category.objects
        .annotate(article_count=Count('articles', filter=Q(articles__status='published')))
        .order_by('order', 'name')
    )
    active_category = Category.objects.filter(slug=category_slug).first() if category_slug else None

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
    from django.db.models import Count
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

    categories = (
        Category.objects
        .annotate(article_count=Count('articles', filter=Q(articles__status='published')))
        .order_by('order', 'name')
    )

    return render(request, 'articles/category.html', {
        'category':    category,
        'articles':    articles,
        'categories':  categories,
        'total_count': paginator.count,
    })


@login_required
def article_request_view(request):
    """Muallif bo'lish uchun zayavka qoldirish (faqat tizimga kirganlar).

    Foydalanuvchi bu yerda o'z zayavkalarining holatini ham ko'radi.
    """
    has_email = bool(request.user.email)

    if request.method == 'POST':
        form = ArticleRequestForm(request.POST, has_email=has_email)
        if form.is_valid():
            article_request = form.save(commit=False)
            article_request.user = request.user
            article_request.full_name = request.user.get_full_name() or request.user.username
            if has_email:
                article_request.email = request.user.email
            article_request.save()
            messages.success(
                request,
                "Zayavkangiz qabul qilindi! Tasdiqlangach, saytda maqola yoza olasiz."
            )
            return redirect('article_request')
        messages.error(request, "Formada xatolik bor. Iltimos, tekshirib qayta yuboring.")
    else:
        form = ArticleRequestForm(has_email=has_email)

    my_requests = request.user.article_requests.order_by('-created_at')

    return render(request, 'articles/request.html', {
        'form': form,
        'my_requests': my_requests,
        'is_author': _is_author(request.user),
    })


# ─────────────────────────────────────────────
# Muallif (ruxsat etilgan foydalanuvchi) sahifalari
# ─────────────────────────────────────────────

def _is_author(user):
    """Faqat muallif flagi bor yoki xodim (staff) foydalanuvchilar."""
    return user.is_authenticated and (getattr(user, 'is_author', False) or user.is_staff)


# login bo'lmaganlar login'ga, ruxsatsizlar 403'ga
author_required = user_passes_test(_is_author, login_url='/login/')


@author_required
def my_articles_view(request):
    """Muallifning o'z maqolalari ro'yxati (boshqaruv paneli)."""
    articles = (
        Article.objects
        .filter(author=request.user)
        .select_related('category')
        .order_by('-updated_at')
    )
    return render(request, 'articles/my_articles.html', {'articles': articles})


@author_required
def article_create_view(request):
    """Saytda yangi maqola yozish (admin panelsiz)."""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            cache.delete('home_page_data')
            messages.success(request, "Maqola saqlandi!")
            return redirect('my_articles')
        messages.error(request, "Formada xatolik bor. Iltimos, tekshirib qayta yuboring.")
    else:
        form = ArticleForm()

    return render(request, 'articles/editor.html', {
        'form': form,
        'is_edit': False,
    })


@author_required
def article_edit_view(request, pk):
    """Muallif o'z maqolasini tahrirlaydi."""
    article = get_object_or_404(Article, pk=pk)
    # Faqat o'z maqolasini yoki staff istalganini tahrirlaydi
    if article.author != request.user and not request.user.is_staff:
        raise Http404()

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            cache.delete('home_page_data')
            messages.success(request, "Maqola yangilandi!")
            return redirect('my_articles')
        messages.error(request, "Formada xatolik bor. Iltimos, tekshirib qayta yuboring.")
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/editor.html', {
        'form': form,
        'is_edit': True,
        'article': article,
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