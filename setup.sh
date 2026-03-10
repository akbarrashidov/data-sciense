#!/bin/bash
# TechBlog - O'rnatish skripti

set -e

echo "================================="
echo "  TechBlog O'rnatish Skripti"
echo "================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 topilmadi. O'rnating!"
    exit 1
fi

# Check pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip topilmadi!"
    exit 1
fi

echo "✅ Python3 mavjud"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Virtual muhit yaratilmoqda..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate
echo "✅ Virtual muhit faollashtirildi"

# Install requirements
echo "📦 Kutubxonalar o'rnatilmoqda..."
pip install -r requirements.txt -q
echo "✅ Kutubxonalar o'rnatildi"

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "⚙️  .env fayl yaratilmoqda..."
    cp .env.example .env
    echo "⚠️  .env fayldagi ma'lumotlarni to'ldiring!"
fi

# Check if .env is configured
echo ""
echo "==========================="
echo "  Ma'lumotlar bazasi sozlash"
echo "==========================="
echo "PostgreSQL ma'lumotlaringizni .env faylga kiriting:"
echo "  DB_NAME=techblog_db"
echo "  DB_USER=postgres"
echo "  DB_PASSWORD=sizning_parol"
echo ""
read -p "PostgreSQL sozlandimi? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    echo "🔄 Migratsiyalar bajarilmoqda..."
    python manage.py makemigrations
    python manage.py migrate
    echo "✅ Migratsiyalar bajarildi"
    
    echo ""
    echo "👤 Superuser yaratish:"
    python manage.py createsuperuser
    
    echo ""
    echo "📊 Namuna kategoriyalar qo'shilmoqda..."
    python manage.py shell -c "
from apps.articles.models import Category
categories = [
    {'name': 'Artificial Intelligence', 'icon': '🤖', 'color': '#6366f1', 'description': 'Sun\'iy intellekt bo\'yicha maqolalar'},
    {'name': 'Machine Learning', 'icon': '🧠', 'color': '#8b5cf6', 'description': 'Machine learning algoritmlari va usullari'},
    {'name': 'Deep Learning', 'icon': '🔮', 'color': '#ec4899', 'description': 'Neyron tarmoqlar va chuqur o\'rganish'},
    {'name': 'Algorithms', 'icon': '⚡', 'color': '#f59e0b', 'description': 'Algoritmlar va ma\'lumotlar tuzilmasi'},
    {'name': 'Python', 'icon': '🐍', 'color': '#22c55e', 'description': 'Python dasturlash tili'},
    {'name': 'Data Science', 'icon': '📊', 'color': '#3b82f6', 'description': 'Ma\'lumotlar tahlili va vizualizatsiya'},
    {'name': 'Computer Vision', 'icon': '👁️', 'color': '#ef4444', 'description': 'Kompyuter ko\'rishi va tasvirni qayta ishlash'},
    {'name': 'NLP', 'icon': '💬', 'color': '#14b8a6', 'description': 'Tabiiy til bilan ishlash'},
]
for cat_data in categories:
    Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
print('Kategoriyalar qo\'shildi!')
" 2>/dev/null || echo "Kategoriyalar qo'shishda xatolik (keyinroq admin orqali qo'shish mumkin)"
    
    echo ""
    echo "✅ O'rnatish tugadi!"
    echo ""
    echo "🚀 Serverni ishga tushirish:"
    echo "   source venv/bin/activate"
    echo "   python manage.py runserver"
    echo ""
    echo "🔗 URL manzillar:"
    echo "   Sayt:  http://localhost:8000"
    echo "   Admin: http://localhost:8000/admin"
else
    echo ""
    echo "⚠️  Avval .env fayldagi DB ma'lumotlarini to'ldiring,"
    echo "   so'ng quyidagi buyruqlarni bajaring:"
    echo ""
    echo "   source venv/bin/activate"
    echo "   python manage.py makemigrations"
    echo "   python manage.py migrate"
    echo "   python manage.py createsuperuser"
    echo "   python manage.py runserver"
fi
