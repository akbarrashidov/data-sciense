"""Header navigatsiyasi uchun context processor.

Yuqori header'dagi bo'limlarni backendda haqiqatan mavjud bo'lgan
ma'lumotlarga bog'laydi — masalan, "Darsliklar" faqat chop etilgan
darslik mavjud bo'lsa, "Mavzular" faqat kategoriya mavjud bo'lsa ko'rinadi.
"""
from django.contrib.auth import get_user_model
from .models import Article, Category

User = get_user_model()

# content_type -> ko'rsatiladigan yorliq (generic "article" alohida "Maqolalar")
_NAV_TYPES = [
    ('tutorial', 'Darsliklar'),
    ('video', 'Video'),
    ('course', 'Kurslar'),
]


def nav(request):
    published = Article.objects.filter(status='published')

    # Chop etilgan maqolalarda mavjud bo'lgan content type'lar
    present = set(published.values_list('content_type', flat=True).distinct())

    nav_content_types = [
        {'type': t, 'label': label, 'url': f'/articles/?type={t}'}
        for t, label in _NAV_TYPES
        if t in present
    ]

    return {
        'nav_has_articles': published.exists(),
        'nav_content_types': nav_content_types,
        'nav_has_categories': Category.objects.filter(
            articles__status='published'
        ).exists(),
        'nav_has_authors': User.objects.filter(
            articles__status='published'
        ).exists(),
    }
