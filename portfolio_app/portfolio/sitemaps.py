from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project, BlogPost


class StaticSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return ['home', 'about', 'contact', 'projects', 'blog']
    
    def location(self, item):
        return reverse(f'portfolio:{item}')


class ProjectSitemap(Sitemap):
    """Sitemap for projects"""
    priority = 0.9
    changefreq = 'monthly'
    
    def items(self):
        return Project.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_at


class BlogSitemap(Sitemap):
    """Sitemap for blog posts"""
    priority = 0.7
    changefreq = 'weekly'
    
    def items(self):
        return BlogPost.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_at