from django.db import models


class PageVisit(models.Model):
    """Saytga har bir tashrif (sahifa ko'rish) yozuvi.

    Ro'yxatdan o'tmagan (anonim) mehmonlar ham yoziladi — noyob mehmonlar
    session_key orqali hisoblanadi. Ro'yxatdan o'tgan foydalanuvchilar
    `user` maydonida bog'lanadi.
    """
    session_key = models.CharField(
        max_length=40, db_index=True, blank=True, verbose_name="Sessiya kaliti"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP manzil"
    )
    user = models.ForeignKey(
        'accounts.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='visits',
        verbose_name="Foydalanuvchi"
    )
    path = models.CharField(max_length=500, verbose_name="Sahifa")
    referer = models.CharField(max_length=500, blank=True, verbose_name="Havola manbasi")
    user_agent = models.CharField(max_length=400, blank=True, verbose_name="Brauzer")
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name="Vaqt"
    )

    class Meta:
        verbose_name = "Tashrif"
        verbose_name_plural = "Tashriflar (statistika)"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at', 'session_key']),
        ]

    def __str__(self):
        who = self.user.username if self.user_id else (self.session_key[:8] or 'anonim')
        return f"{who} → {self.path}"

    @property
    def is_guest(self):
        return self.user_id is None
