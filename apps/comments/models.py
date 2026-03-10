from django.db import models


class Comment(models.Model):
    article = models.ForeignKey(
        'articles.Article', on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies'
    )
    text = models.TextField(verbose_name="Fikr")
    is_approved = models.BooleanField(default=True, verbose_name="Tasdiqlangan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fikr"
        verbose_name_plural = "Fikrlar"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username}: {self.text[:50]}"
