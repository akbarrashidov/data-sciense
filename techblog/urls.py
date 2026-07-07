from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic.base import RedirectView

# Favicon — ildizdagi /favicon.ico so'rovini haqiqiy statik faylga yo'naltiradi
# (Google qidiruv natijalarida ikonka ko'rinishi uchun zarur)
favicon_view = RedirectView.as_view(
    url=settings.STATIC_URL + 'favicon/favicon.ico', permanent=True
)

urlpatterns = [
    path('favicon.ico', favicon_view),
    path('admin/', admin.site.urls),
    path('mdeditor/', include('mdeditor.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('api/', include('apps.articles.api_urls')),
    path('api/auth/', include('apps.accounts.api_urls')),
    path('api/comments/', include('apps.comments.api_urls')),
    path('accounts/', include('allauth.urls')),  # Google OAuth (allauth)
    path('', include('apps.articles.urls')),
    path('', include('apps.accounts.urls')),
]

# DEBUG=False da ham media va static ishlashi uchun
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'techblog.views.custom_404'
