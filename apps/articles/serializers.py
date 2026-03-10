from rest_framework import serializers
from .models import Article, Category, Rating
from apps.accounts.serializers import UserPublicSerializer


class CategorySerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 'article_count']

    def get_article_count(self, obj):
        return obj.get_article_count()


class ArticleListSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'content_type',
            'thumbnail', 'excerpt', 'status', 'is_featured', 'views_count',
            'read_time', 'tags_list', 'average_rating', 'rating_count',
            'comment_count', 'published_at', 'created_at',
        ]

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_rating_count(self, obj):
        return obj.get_rating_count()

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_tags_list(self, obj):
        return obj.get_tags_list()


class ArticleDetailSerializer(ArticleListSerializer):
    youtube_embed = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + ['content', 'youtube_url', 'youtube_embed', 'updated_at']

    def get_youtube_embed(self, obj):
        return obj.get_youtube_embed()


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'score', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        article = self.context['article']
        rating, created = Rating.objects.update_or_create(
            user=user, article=article,
            defaults={'score': validated_data['score']}
        )
        return rating
