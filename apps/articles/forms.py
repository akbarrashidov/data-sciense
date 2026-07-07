from django import forms

from .models import ArticleRequest, Article, ArticleStatus


class ArticleRequestForm(forms.ModelForm):
    """Muallif bo'lish uchun zayavka formasi.

    Faqat "o'zingiz haqingizda" va email so'raydi. Foydalanuvchining emaili
    allaqachon bo'lsa (`has_email=True`), faqat "o'zingiz haqingizda" so'raladi.
    """

    class Meta:
        model = ArticleRequest
        fields = ['email', 'message']
        labels = {
            'message': "O'zingiz haqingizda",
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@example.com',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 6,
                'placeholder': "Tajribangiz, qanday mavzularda yozmoqchisiz, o'zingiz haqingizda…",
            }),
        }

    def __init__(self, *args, has_email=False, **kwargs):
        super().__init__(*args, **kwargs)
        # Foydalanuvchida email bo'lsa — uni so'ramaymiz
        if has_email:
            self.fields.pop('email', None)


class ArticleForm(forms.ModelForm):
    """Saytda maqola yozish/tahrirlash formasi (ruxsat etilgan mualliflar uchun).

    `content` maydoni model `MDTextField` bo'lgani uchun avtomatik ravishda
    admin paneldagidek to'liq funksiyali MDEditor (Markdown + LaTeX) bilan
    render qilinadi.
    """

    class Meta:
        model = Article
        fields = [
            'title', 'category', 'content_type', 'status',
            'thumbnail', 'excerpt', 'youtube_url', 'tags', 'content',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Maqola sarlavhasi',
            }),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'content_type': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': "Qisqacha tavsif (ro'yxatlarda va qidiruvda ko'rinadi)",
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://youtube.com/watch?v=… (video uchun, ixtiyoriy)',
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'python, machine learning, nlp (vergul bilan)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].empty_label = "Kategoriya tanlang"

        # Muallif maqolani CHOP ETA OLMAYDI. U faqat qoralama saqlaydi yoki
        # ko'rib chiqishga yuboradi. Chop etishni admin panel orqali admin qiladi.
        self.fields['status'].choices = [
            (ArticleStatus.DRAFT, 'Qoralama (faqat siz ko\'rasiz)'),
            (ArticleStatus.PENDING, 'Ko\'rib chiqishga yuborish'),
        ]

        # Agar maqola admin tomonidan allaqachon chop etilgan bo'lsa —
        # muallif uni tahrirlaganda holatni o'zgartira olmaydi (chop etilgan qoladi).
        if self.instance and self.instance.pk and self.instance.status == ArticleStatus.PUBLISHED:
            self.fields['status'].choices = [
                (ArticleStatus.PUBLISHED, 'Chop etilgan (admin tomonidan)'),
            ]
            self.fields['status'].disabled = True
