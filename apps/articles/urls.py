from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('articles/', views.article_list_view, name='article_list'),
    path('articles/<slug:slug>/', views.article_detail_view, name='article_detail'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
]
