from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import viewsets

router = DefaultRouter()
router.register(r'projects', viewsets.ProjectViewSet)
router.register(r'blog-posts', viewsets.BlogPostViewSet)
router.register(r'skills', viewsets.SkillViewSet)
router.register(r'categories', viewsets.CategoryViewSet)
router.register(r'contact', viewsets.ContactViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]