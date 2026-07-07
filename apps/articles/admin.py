from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.contrib import messages
from .models import Category, Article, Rating, ArticleRequest, ArticleRequestStatus


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'order', 'get_article_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'color']

    def get_article_count(self, obj):
        return obj.get_article_count()
    get_article_count.short_description = "Maqolalar soni"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 35,
            'cols': 100,
            'style': 'font-family: monospace; font-size: 14px;'
        })},
    }
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


@admin.register(ArticleRequest)
class ArticleRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'email', 'about_preview', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'email', 'message', 'user__username']
    list_editable = ['status']
    list_select_related = ['user']
    readonly_fields = ['user', 'full_name', 'email', 'message', 'created_at', 'updated_at']
    list_per_page = 30
    date_hierarchy = 'created_at'
    actions = ['accept_requests', 'reject_requests']

    @admin.display(description="O'zi haqida")
    def about_preview(self, obj):
        return (obj.message[:70] + '…') if len(obj.message) > 70 else obj.message

    @admin.action(description="Tanlangan zayavkalarni qabul qilish (muallif huquqini berish)")
    def accept_requests(self, request, queryset):
        granted = 0
        for req in queryset:
            req.status = ArticleRequestStatus.ACCEPTED
            req.save()  # save() muallif huquqini avtomatik yoqadi
            if req.user_id:
                granted += 1
        self.message_user(
            request,
            f"{queryset.count()} ta zayavka qabul qilindi, {granted} ta foydalanuvchiga muallif huquqi berildi.",
            messages.SUCCESS,
        )

    @admin.action(description="Tanlangan zayavkalarni rad etish")
    def reject_requests(self, request, queryset):
        updated = queryset.update(status=ArticleRequestStatus.REJECTED)
        self.message_user(request, f"{updated} ta zayavka rad etildi.", messages.SUCCESS)

    fieldsets = (
        ('Zayavka', {
            'fields': ('user', 'full_name', 'email', 'message')
        }),
        ('Ko\'rib chiqish', {
            'fields': ('status', 'admin_note', 'created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        # Zayavkalar faqat saytdagi forma orqali yaratiladi
        return False