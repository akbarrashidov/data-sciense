from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended User with portfolio fields"""
    bio = models.TextField(blank=True, verbose_name="Haqida")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Rasm")
    profession = models.CharField(max_length=200, blank=True, verbose_name="Kasbi")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    github = models.URLField(blank=True, verbose_name="GitHub")
    telegram = models.CharField(max_length=100, blank=True, verbose_name="Telegram (@username)")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    facebook = models.URLField(blank=True, verbose_name="Facebook")
    instagram = models.CharField(max_length=100, blank=True, verbose_name="Instagram (@username)")
    twitter = models.URLField(blank=True, verbose_name="Twitter/X")
    website = models.URLField(blank=True, verbose_name="Shaxsiy sayt")
    location = models.CharField(max_length=200, blank=True, verbose_name="Joylashuv")
    skills = models.TextField(blank=True, verbose_name="Ko'nikmalar (vergul bilan)")

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return self.get_full_name() or self.username

    def get_article_count(self):
        return self.articles.filter(status='published').count()

    def get_skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []

    def get_telegram_url(self):
        if self.telegram:
            username = self.telegram.lstrip('@')
            return f"https://t.me/{username}"
        return ''

    def get_instagram_url(self):
        if self.instagram:
            username = self.instagram.lstrip('@')
            return f"https://instagram.com/{username}"
        return ''
