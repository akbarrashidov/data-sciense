from rest_framework import serializers
from .models import User


class UserPublicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    article_count = serializers.SerializerMethodField()
    skills_list = serializers.SerializerMethodField()
    telegram_url = serializers.SerializerMethodField()
    instagram_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'bio', 'avatar', 'profession',
            'phone', 'location', 'skills_list', 'github', 'telegram', 'telegram_url',
            'linkedin', 'facebook', 'instagram', 'instagram_url', 'twitter', 'website',
            'article_count', 'date_joined',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_article_count(self, obj):
        return obj.get_article_count()

    def get_skills_list(self, obj):
        return obj.get_skills_list()

    def get_telegram_url(self, obj):
        return obj.get_telegram_url()

    def get_instagram_url(self, obj):
        return obj.get_instagram_url()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Parollar mos kelmadi")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
