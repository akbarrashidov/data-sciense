from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.ArticleCommentsAPIView.as_view(), name='api_comments'),
    path('delete/<int:pk>/', views.CommentDeleteAPIView.as_view(), name='api_comment_delete'),
]
