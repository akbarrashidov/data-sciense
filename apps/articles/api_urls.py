from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListAPIView.as_view(), name='api_categories'),
    path('articles/', views.ArticleListAPIView.as_view(), name='api_articles'),
    path('articles/<slug:slug>/', views.ArticleDetailAPIView.as_view(), name='api_article_detail'),
    path('articles/<slug:slug>/rate/', views.RateArticleAPIView.as_view(), name='api_rate_article'),
]
