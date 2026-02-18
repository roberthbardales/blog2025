from rest_framework import serializers
from .models import Entry, Category, Tag, Comment, Like
from applications.users.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'full_name',
        )



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'short_name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'content',
            'parent',
            'replies',
            'created',
        )

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data


class EntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer()
    tag = TagSerializer(many=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = Entry
        fields = (
            'id',
            'title',
            'resume',
            'content',
            'slug',
            'image',
            'user',
            'category',
            'tag',
            'likes_count',
            'created',
        )


class EntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = (
            'title',
            'resume',
            'content',
            'category',
            'tag',
            'image',
            'public',
        )
