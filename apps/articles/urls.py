from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('maqola-taklif/', views.article_request_view, name='article_request'),
    path('yozish/', views.article_create_view, name='article_create'),
    path('yozish/mening-maqolalarim/', views.my_articles_view, name='my_articles'),
    path('yozish/<uuid:pk>/', views.article_edit_view, name='article_edit'),
    path('articles/', views.article_list_view, name='article_list'),
    path('articles/<slug:slug>/', views.article_detail_view, name='article_detail'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
]
