from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import PageVisit


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'who', 'path', 'ip_address', 'referer']
    list_filter = ['created_at', ('user', admin.EmptyFieldListFilter)]
    search_fields = ['path', 'ip_address', 'session_key', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = [
        'session_key', 'ip_address', 'user', 'path',
        'referer', 'user_agent', 'created_at',
    ]

    # Statistika faqat ko'rish uchun — qo'lda yozib bo'lmaydi
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Kim")
    def who(self, obj):
        if obj.user_id:
            return f"👤 {obj.user.username}"
        return f"🕵️ mehmon ({obj.session_key[:8] or '—'})"

    def changelist_view(self, request, extra_context=None):
        """O'ng tepaga umumiy statistika kartalarini qo'shadi."""
        extra_context = extra_context or {}

        now = timezone.now()
        today = now.date()
        week_ago = now - timezone.timedelta(days=7)
        month_ago = now - timezone.timedelta(days=30)

        qs = PageVisit.objects.all()

        def stats(queryset):
            return {
                'views': queryset.count(),
                'visitors': queryset.values('session_key').distinct().count(),
            }

        # So'nggi 14 kunlik kunlik grafik uchun ma'lumot
        daily_raw = (
            qs.filter(created_at__gte=now - timezone.timedelta(days=14))
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(
                views=Count('id'),
                visitors=Count('session_key', distinct=True),
            )
            .order_by('day')
        )
        max_views = max([d['views'] for d in daily_raw], default=1) or 1
        daily = [
            {
                'day': d['day'],
                'views': d['views'],
                'visitors': d['visitors'],
                'pct': round(d['views'] / max_views * 100),
            }
            for d in daily_raw
        ]

        extra_context['visit_stats'] = {
            'today': stats(qs.filter(created_at__date=today)),
            'week': stats(qs.filter(created_at__gte=week_ago)),
            'month': stats(qs.filter(created_at__gte=month_ago)),
            'total': stats(qs),
            'guest_views': qs.filter(user__isnull=True).count(),
            'user_views': qs.filter(user__isnull=False).count(),
            'daily': daily,
            'top_pages': list(
                qs.values('path')
                .annotate(views=Count('id'))
                .order_by('-views')[:10]
            ),
        }
        return super().changelist_view(request, extra_context=extra_context)
