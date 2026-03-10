from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration/', views.register_page, name='register_page'),
    path('author/<str:username>/', views.author_profile, name='author_profile'),

    path('api/register/', views.RegisterView.as_view(), name='register_api'),
    path('api/author/<str:username>/', views.UserProfileAPIView.as_view(), name='author_api'),
]