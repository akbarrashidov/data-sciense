from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .models import Article, Category, Rating
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer,
    CategorySerializer, RatingSerializer
)


# Template Views
def home_view(request):
    featured = Article.objects.filter(status='published', is_featured=True)[:3]
    latest = Article.objects.filter(status='published').select_related('author', 'category')[:12]
    categories = Category.objects.all()
    tutorials = Article.objects.filter(status='published', content_type__in=['tutorial', 'video', 'course'])[:6]
    return render(request, 'articles/home.html', {
        'featured': featured,
        'latest': latest,
        'categories': categories,
        'tutorials': tutorials,
    })


def article_list_view(request):
    queryset = Article.objects.filter(status='published').select_related('author', 'category')
    category_slug = request.GET.get('category')
    content_type = request.GET.get('type')
    search = request.GET.get('q')

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

    categories = Category.objects.all()
    active_category = Category.objects.filter(slug=category_slug).first() if category_slug else None

    return render(request, 'articles/list.html', {
        'articles': queryset,
        'categories': categories,
        'active_category': active_category,
        'content_type': content_type,
        'search': search,
    })


def article_detail_view(request, slug):
    article = get_object_or_404(Article, slug=slug, status='published')
    # Increment views
    Article.objects.filter(pk=article.pk).update(views_count=article.views_count + 1)
    article.refresh_from_db()

    comments = article.comments.filter(is_approved=True).select_related('author').order_by('created_at')
    related = Article.objects.filter(
        status='published', category=article.category
    ).exclude(pk=article.pk)[:4]

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(article=article, user=request.user).first()

    return render(request, 'articles/detail.html', {
        'article': article,
        'comments': comments,
        'related': related,
        'user_rating': user_rating,
        'average_rating': article.get_average_rating(),
        'rating_count': article.get_rating_count(),
    })


def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(status='published', category=category).select_related('author')
    categories = Category.objects.all()
    return render(request, 'articles/category.html', {
        'category': category,
        'articles': articles,
        'categories': categories,
    })


# REST API Views
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ArticleListAPIView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['published_at', 'views_count', 'created_at']

    def get_queryset(self):
        qs = Article.objects.filter(status='published').select_related('author', 'category')
        category = self.request.query_params.get('category')
        content_type = self.request.query_params.get('type')
        if category:
            qs = qs.filter(category__slug=category)
        if content_type:
            qs = qs.filter(content_type=content_type)
        return qs


class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(status='published')
    serializer_class = ArticleDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


class RateArticleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug, status='published')
        serializer = RatingSerializer(
            data=request.data,
            context={'request': request, 'article': article}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'average_rating': article.get_average_rating(),
                'rating_count': article.get_rating_count(),
                'user_rating': serializer.data['score'],
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
