from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Category, Article, Rating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'order', 'get_article_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'color']

    def get_article_count(self, obj):
        return obj.get_article_count()
    get_article_count.short_description = "Maqolalar soni"


@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ['title', 'author', 'category', 'content_type', 'status', 'is_featured', 'views_count', 'created_at']
    list_filter = ['status', 'content_type', 'category', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured']
    readonly_fields = ['views_count', 'read_time', 'created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        ('Asosiy', {
            'fields': ('title', 'slug', 'author', 'category', 'content_type', 'status', 'is_featured')
        }),
        ('Kontent', {
            'fields': ('thumbnail', 'excerpt', 'content', 'youtube_url', 'tags')
        }),
        ('Statistika', {
            'fields': ('views_count', 'read_time', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'score', 'created_at']
    list_filter = ['score']
