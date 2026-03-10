# ⚡ TechBlog - AI, ML va Algoritmlar Platformasi

Django + REST API + PostgreSQL bilan qurilgan to'liq blog platformasi.

---

## 🚀 Tezkor O'rnatish

```bash
# 1. Loyihani yuklab oling
cd techblog

# 2. Setup skriptini ishga tushiring
chmod +x setup.sh
./setup.sh
```

---

## 📋 Qo'lda O'rnatish

### Talablar
- Python 3.9+
- PostgreSQL 13+

### Qadamlar

```bash
# 1. Virtual muhit
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. .env fayl
cp .env.example .env
# .env faylni tahrirlang!

# 4. PostgreSQL bazani yarating
psql -U postgres -c "CREATE DATABASE techblog_db;"

# 5. Migratsiyalar
python manage.py makemigrations
python manage.py migrate

# 6. Superuser
python manage.py createsuperuser

# 7. Namuna kategoriyalar (ixtiyoriy)
python manage.py shell < scripts/add_categories.py

# 8. Serverni ishga tushiring
python manage.py runserver
```

---

## 🌐 URL Manzillar

| URL | Tavsif |
|-----|--------|
| `http://localhost:8000/` | Bosh sahifa |
| `http://localhost:8000/articles/` | Barcha maqolalar |
| `http://localhost:8000/articles/?type=tutorial` | Darsliklar |
| `http://localhost:8000/articles/?type=video` | Video darsliklar |
| `http://localhost:8000/category/<slug>/` | Kategoriya |
| `http://localhost:8000/articles/<slug>/` | Maqola tafsilotlari |
| `http://localhost:8000/author/<username>/` | Muallif profili |
| `http://localhost:8000/login/` | Kirish |
| `http://localhost:8000/admin/` | Admin panel |

---

## 🔌 REST API Endpointlar

```
GET  /api/categories/                    - Kategoriyalar ro'yxati
GET  /api/articles/                      - Maqolalar ro'yxati
GET  /api/articles/?category=ml          - Kategoriya bo'yicha filtrlash
GET  /api/articles/?type=tutorial        - Tur bo'yicha filtrlash
GET  /api/articles/?search=neural        - Qidiruv
GET  /api/articles/<slug>/               - Maqola tafsilotlari
POST /api/articles/<slug>/rate/          - Baholash (token kerak)

GET  /api/comments/<slug>/               - Fikrlar ro'yxati
POST /api/comments/<slug>/               - Fikr qo'shish (token kerak)
DELETE /api/comments/delete/<id>/        - Fikr o'chirish (token kerak)

POST /api/auth/login/                    - JWT token olish
POST /api/auth/register/                 - Ro'yxatdan o'tish
POST /api/auth/refresh/                  - Token yangilash
GET  /api/auth/users/<username>/         - Foydalanuvchi profili
```

---

## 👤 Foydalanuvchi Turlari

### Admin (Staff)
- Django admin orqali maqola va darslik qo'shish
- Summernote WYSIWYG editor: rasm, video, kod, matematik formula
- Kategoriyalarni boshqarish
- Fikrlarni tasdiqlash/o'chirish
- Maqola statusini boshqarish: `qoralama → kutilmoqda → nashr`

### Oddiy Foydalanuvchi
- Maqola va darsliklarni o'qish
- Fikr bildirish va javob berish
- Maqolalarni baholash (1-5 yulduz)
- Muallif profilini ko'rish

---

## 📝 Maqola Holatlari

```
draft (Qoralama)  →  pending (Kutilmoqda)  →  published (Nashr)
```

Faqat `published` holatidagi maqolalar frontendda ko'rinadi.

---

## ✏️ Summernote Editor Imkoniyatlari

Admin panelida maqola yaratishda:
- **Matn formatlash**: qalin, kursiv, tagchiziq, o'chirib o'tish
- **Shriftlar va o'lchamlar**: turli xil font va o'lcham tanlash
- **Ranglar**: matn va fon rangi
- **Ro'yxatlar**: tartiblangan va tartiblanmagan
- **Jadvallar**: dinamik jadval qo'shish
- **Rasmlar**: yuklash va URL orqali qo'shish
- **Videolar**: YouTube va boshqa manzillar (iframe)
- **Kod**: kod bloklari
- **HTML ko'rish**: to'g'ridan-to'g'ri HTML tahrirlash

### Matematik Formulalar

Frontendda KaTeX orqali render qilinadi:

```
Inline: $E = mc^2$
Block:  $$\sum_{i=1}^{n} x_i = \frac{n(n+1)}{2}$$
LaTeX:  \[f(x) = \int_{-\infty}^{\infty} \hat{f}(\xi) e^{2\pi i \xi x} d\xi\]
```

---

## 🎨 Funksiyalar

- ✅ Dark/Light tema
- ✅ Responsive dizayn (mobil, planshet, desktop)
- ✅ Maqolada o'qish progress bar
- ✅ Kod bloklarida nusxa olish tugmasi
- ✅ Muallif portfolio sahifasi
- ✅ Ijtimoiy tarmoq havolalari
- ✅ YouTube embed qo'llab-quvvatlash
- ✅ Matematik formulalar (KaTeX)
- ✅ Sintaksis rang berish (Highlight.js)
- ✅ Maqola ichida mundarija (TOC)
- ✅ O'xshash maqolalar
- ✅ Fikrlar va javoblar (nested)
- ✅ Yulduzli baholash tizimi
- ✅ Kategoriya bo'yicha filtrlash
- ✅ Qidiruv

---

## 🏗️ Loyiha Tuzilishi

```
techblog/
├── apps/
│   ├── accounts/     # Foydalanuvchi modeli va portfolio
│   ├── articles/     # Maqola, kategoriya, baholash
│   └── comments/     # Fikrlar tizimi
├── static/
│   ├── css/main.css  # Asosiy stil
│   └── js/main.js    # Asosiy JavaScript
├── templates/
│   ├── base.html
│   ├── accounts/     # Login, profil
│   ├── articles/     # Bosh sahifa, ro'yxat, tafsilot
│   └── components/   # Qayta ishlatiladigan qismlar
├── techblog/         # Django sozlamalari
├── .env.example
├── requirements.txt
└── setup.sh
```

---

## 📦 Texnologiyalar

| Texnologiya | Versiya | Maqsad |
|------------|---------|--------|
| Django | 4.2 | Backend framework |
| Django REST Framework | 3.14 | REST API |
| PostgreSQL | 13+ | Ma'lumotlar bazasi |
| django-summernote | 0.8 | WYSIWYG editor |
| KaTeX | 0.16 | Matematik formulalar |
| Highlight.js | 11.9 | Kod rang berish |
| Font Awesome | 6.5 | Ikonlar |
| JWT | simplejwt | Autentifikatsiya |
