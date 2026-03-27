from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import HttpResponse

# Favicon
def favicon(request):
    return HttpResponse(status=204)

urlpatterns = [
    path('favicon.ico', favicon),
    path('admin/', admin.site.urls),
    path('mdeditor/', include('mdeditor.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('api/', include('apps.articles.api_urls')),
    path('api/auth/', include('apps.accounts.api_urls')),
    path('api/comments/', include('apps.comments.api_urls')),
    path('', include('apps.articles.urls')),
    path('', include('apps.accounts.urls')),
]

# DEBUG=False da ham media va static ishlashi uchun
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'techblog.views.custom_404'
