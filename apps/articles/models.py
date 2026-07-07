from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from mdeditor.fields import MDTextField
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Tavsif")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon (CSS class yoki emoji)")
    color = models.CharField(max_length=20, default='#6366f1', verbose_name="Rang (hex)")
    order = models.IntegerField(default=0, verbose_name="Tartib")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def get_article_count(self):
        return self.articles.filter(status='published').count()


class ContentType(models.TextChoices):
    ARTICLE = 'article', 'Maqola'
    TUTORIAL = 'tutorial', 'Darslik'
    VIDEO = 'video', 'Video darslik'
    COURSE = 'course', 'Kurs'


class ArticleStatus(models.TextChoices):
    DRAFT = 'draft', 'Qoralama'
    PENDING = 'pending', 'Kutilmoqda'
    PUBLISHED = 'published', 'Chop etilgan'


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300, verbose_name="Sarlavha")
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    author = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='articles', verbose_name="Muallif"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='articles', verbose_name="Kategoriya"
    )
    content_type = models.CharField(
        max_length=20, choices=ContentType.choices,
        default=ContentType.ARTICLE, verbose_name="Tur"
    )
    thumbnail = models.ImageField(
        upload_to='thumbnails/', blank=True, null=True,
        verbose_name="Muqova rasmi"
    )
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Qisqacha tavsif")
    content  = MDTextField(verbose_name="Kontent (Markdown + LaTeX)")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube URL (video uchun)")
    status = models.CharField(
        max_length=20, choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT, verbose_name="Holat"
    )
    is_featured = models.BooleanField(default=False, verbose_name="Tavsiya etilgan")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar")
    read_time = models.PositiveIntegerField(default=5, verbose_name="O'qish vaqti (daqiqa)")
    tags = models.CharField(max_length=500, blank=True, verbose_name="Teglar (vergul bilan)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Nashr vaqti")

    class Meta:
        verbose_name = "Maqola"
        verbose_name_plural = "Maqolalar"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = str(self.id)[:8]
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()

        if self.content:
            word_count = len(self.content.split())
            self.read_time = max(1, word_count // 200)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def get_average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 1)
        return 0

    def get_rating_count(self):
        return self.ratings.count()

    def get_tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    def get_youtube_embed(self):
        """Convert YouTube URL to embed URL"""
        if not self.youtube_url:
            return ''
        url = self.youtube_url
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
        elif 'watch?v=' in url:
            video_id = url.split('watch?v=')[-1].split('&')[0]
        elif 'embed/' in url:
            return url
        else:
            return url
        return f"https://www.youtube.com/embed/{video_id}"


class ArticleRequestStatus(models.TextChoices):
    NEW       = 'new', 'Yangi'
    IN_REVIEW = 'in_review', "Ko'rib chiqilmoqda"
    ACCEPTED  = 'accepted', 'Qabul qilindi'
    REJECTED  = 'rejected', 'Rad etildi'


class ArticleRequest(models.Model):
    """Foydalanuvchi qoldirgan "maqola yozish" zayavkasi.

    Saytdagi forma orqali (faqat tizimga kirgan foydalanuvchilar) to'ldiriladi
    va admin panelda ko'rinadi.
    """
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='article_requests', verbose_name="Foydalanuvchi"
    )
    full_name = models.CharField(max_length=150, blank=True, verbose_name="Ism-familiya")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="O'zi haqida")
    status = models.CharField(
        max_length=20, choices=ArticleRequestStatus.choices,
        default=ArticleRequestStatus.NEW, verbose_name="Holat"
    )
    admin_note = models.TextField(blank=True, verbose_name="Admin izohi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")

    class Meta:
        verbose_name = "Maqola zayavkasi"
        verbose_name_plural = "Maqola zayavkalari"
        ordering = ['-created_at']

    def __str__(self):
        who = self.full_name or (self.user.username if self.user_id else self.email)
        return f"{who} — muallif zayavkasi"

    def save(self, *args, **kwargs):
        # Oldingi holatni aniqlaymiz — faqat "Qabul qilindi"ga O'TGANDA
        # (bir marta) email yuborish uchun.
        old_status = None
        if self.pk:
            old_status = (
                ArticleRequest.objects
                .filter(pk=self.pk)
                .values_list('status', flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        became_accepted = (
            self.status == ArticleRequestStatus.ACCEPTED
            and old_status != ArticleRequestStatus.ACCEPTED
        )
        if became_accepted and self.user_id:
            # Muallif huquqini avtomatik beramiz
            if not self.user.is_author:
                self.user.is_author = True
                self.user.save(update_fields=['is_author'])
            # Foydalanuvchiga xabar yuboramiz
            self._notify_accepted()

    def _notify_accepted(self):
        """Zayavka qabul qilinganini email orqali bildiradi."""
        if not self.user or not self.user.email:
            return
        from django.conf import settings
        from django.core.mail import send_mail

        name = self.user.get_full_name() or self.user.username
        write_url = f"{settings.SITE_URL.rstrip('/')}/yozish/"
        subject = "Zayavkangiz qabul qilindi — DataScience"
        message = (
            f"Assalomu alaykum, {name}!\n\n"
            f"Muallif bo'lish uchun zayavkangiz qabul qilindi. "
            f"Endi siz DataScience platformasida to'g'ridan-to'g'ri maqola yoza olasiz.\n\n"
            f"Maqola yozishni boshlash: {write_url}\n\n"
            f"Eslatma: maqolani qoralama saqlashingiz yoki ko'rib chiqishga "
            f"yuborishingiz mumkin. Chop etishni administratorlar amalga oshiradi.\n\n"
            f"Hurmat bilan,\nDataScience jamoasi"
        )
        # Email xatosi admin paneldagi saqlashni buzmasligi uchun fail_silently
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL,
            [self.user.email], fail_silently=True,
        )


class Rating(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    score = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')
        verbose_name = "Baholash"
        verbose_name_plural = "Baholashlar"

    def __str__(self):
        return f"{self.user.username} → {self.article.title}: {self.score}"
