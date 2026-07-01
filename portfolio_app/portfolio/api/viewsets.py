from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from portfolio.models import Project, BlogPost, Skill, ContactMessage
from .serializers import (
    ProjectSerializer, BlogPostSerializer, SkillSerializer,
    ContactMessageSerializer, CategorySerializer
)
from portfolio.models import Category
from portfolio.services import ContactService


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for projects"""
    queryset = Project.objects.filter(status='published')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'featured', 'status']
    search_fields = ['title', 'short_description', 'description', 'technologies']
    ordering_fields = ['created_at', 'views_count', 'title']
    ordering = ['-created_at']


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for blog posts"""
    queryset = BlogPost.objects.filter(status='published')
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'author__username']
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'views_count', 'likes_count']
    ordering = ['-published_at']
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes_count += 1
        post.save(update_fields=['likes_count'])
        return Response({'likes_count': post.likes_count})


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for skills"""
    queryset = Skill.objects.filter(is_active=True)
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'proficiency']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'proficiency', 'years_of_experience']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']


class ContactViewSet(viewsets.GenericViewSet):
    """API endpoint for contact form"""
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        success, message = ContactService.save_contact_message(
            serializer.validated_data,
            request
        )
        
        if success:
            return Response(
                {'message': 'Your message has been sent successfully!'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Unable to send message. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )