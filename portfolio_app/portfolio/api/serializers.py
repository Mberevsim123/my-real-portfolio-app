from rest_framework import serializers
from portfolio.models import Project, BlogPost, Skill, ContactMessage, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']


class SkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    proficiency_display = serializers.CharField(source='get_proficiency_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'category_name', 'proficiency', 
                  'proficiency_display', 'icon', 'years_of_experience', 'description']


class ProjectSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    technologies_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'short_description', 'description',
            'technologies', 'technologies_list', 'category', 'category_name',
            'github_url', 'live_url', 'documentation_url', 'image',
            'video_url', 'featured', 'views_count', 'created_at'
        ]
    
    def get_technologies_list(self, obj):
        return obj.get_technologies_list()


class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featured_image',
            'category', 'category_name', 'author', 'author_name', 'tags_list',
            'published_at', 'views_count', 'likes_count', 'read_time'
        ]
    
    def get_tags_list(self, obj):
        return [tag.name for tag in obj.tags.all()]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'custom_subject', 'message']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            validated_data['ip_address'] = ip
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        return super().create(validated_data)