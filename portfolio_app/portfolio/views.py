from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, FormView, View
from .models import (
    Project, BlogPost, Skill, Category, ContactMessage,
    Education, WorkExperience, Certification, SocialLink
)
from .forms import ContactForm, NewsletterForm, CommentForm, SearchForm
from .services import (
    PortfolioService, ContactService, NewsletterService,
    AnalyticsService, CommentService, SEOService
)
import logging

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Cache heavy queries for 5 minutes
        cache_key = 'homepage_data'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            context.update(cached_data)
        else:
            data = {
                'featured_projects': PortfolioService.get_featured_projects(6),
                'recent_blog_posts': PortfolioService.get_recent_blog_posts(3),
                'skills': Skill.objects.filter(is_active=True).select_related('category'),
                'featured_skills': Skill.objects.filter(is_active=True, proficiency__gte=4)[:12],
                'categories': Category.objects.annotate(project_count=Count('projects')),
                'work_experience': WorkExperience.objects.all(),
                'education': Education.objects.all(),
                'certifications': Certification.objects.all()[:6],
                'total_projects': Project.objects.filter(status='published').count(),
                'total_blog_posts': BlogPost.objects.filter(status='published').count(),
                'total_skills': Skill.objects.filter(is_active=True).count(),
            }
            cache.set(cache_key, data, 300)  # Cache for 5 minutes
            context.update(data)
        
        # Newsletter form
        context['newsletter_form'] = NewsletterForm()
        
        # Track analytics
        AnalyticsService.track_visit(self.request, self.request.path)
        
        return context


class AboutView(TemplateView):
    """About page view"""
    template_name = 'portfolio/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Cache about page data
        cache_key = 'about_page_data'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            context.update(cached_data)
        else:
            data = {
                'skills': Skill.objects.filter(is_active=True).select_related('category'),
                'work_experience': WorkExperience.objects.all(),
                'education': Education.objects.all(),
                'certifications': Certification.objects.all(),
                'social_links': SocialLink.objects.filter(is_active=True),
                'years_of_experience': self.calculate_years_experience(),
            }
            cache.set(cache_key, data, 3600)  # Cache for 1 hour
            context.update(data)
        
        AnalyticsService.track_visit(self.request, self.request.path)
        
        return context
    
    def calculate_years_experience(self):
        """Calculate total years of professional experience"""
        work_experiences = WorkExperience.objects.all()
        total_days = 0
        
        for exp in work_experiences:
            if exp.is_current:
                end_date = timezone.now().date()
            else:
                end_date = exp.end_date
            
            if exp.start_date and end_date:
                delta = end_date - exp.start_date
                total_days += delta.days
        
        return round(total_days / 365, 1)


class ProjectListView(ListView):
    """Project listing page with filtering and search"""
    model = Project
    template_name = 'portfolio/project_list.html'
    context_object_name = 'projects'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Project.objects.filter(status='published')
        
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(technologies__icontains=search_query)
            )
        
        # Filter by technology
        tech_filter = self.request.GET.get('technology')
        if tech_filter:
            queryset = queryset.filter(technologies__icontains=tech_filter)
        
        # Ordering
        order_by = self.request.GET.get('order', '-created_at')
        if order_by in ['created_at', '-created_at', 'title', '-title', 'views_count', '-views_count']:
            queryset = queryset.order_by(order_by)
        
        return queryset.select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all unique technologies from projects
        technologies = set()
        for project in Project.objects.filter(status='published'):
            technologies.update(project.get_technologies_list())
        
        context['technologies'] = sorted(list(technologies))
        context['search_form'] = SearchForm(self.request.GET)
        context['current_category'] = self.kwargs.get('category_slug')
        context['current_order'] = self.request.GET.get('order', '-created_at')
        
        AnalyticsService.track_visit(self.request, self.request.path)
        
        return context


class ProjectDetailView(DetailView):
    """Project detail page"""
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return Project.objects.filter(slug=self.kwargs['slug'], status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Increment view count
        self.object.increment_views()
        
        # Get related projects
        context['related_projects'] = PortfolioService.get_related_projects(self.object)
        
        # Get additional images
        context['additional_images'] = self.object.additional_images.all()
        
        # SEO meta tags
        context['meta_tags'] = SEOService.get_meta_tags(self.object)
        
        AnalyticsService.track_visit(self.request, self.request.path)
        
        return context


class BlogListView(ListView):
    """Blog listing page"""
    model = BlogPost
    template_name = 'portfolio/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        )
        
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        # Filter by tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__name__iexact=tag)
        
        return queryset.select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all tags
        from taggit.models import Tag
        context['all_tags'] = Tag.objects.all()
        context['popular_tags'] = Tag.objects.annotate(
            num_posts=Count('taggit_taggeditem_items')
        ).order_by('-num_posts')[:15]
        
        context['popular_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-views_count')[:5]
        
        context['search_form'] = SearchForm(self.request.GET)
        
        AnalyticsService.track_visit(self.request, self.request.path)
        
        return context


class BlogDetailView(DetailView):
    """Blog post detail page"""
    model = BlogPost
    template_name = 'portfolio/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(slug=self.kwargs['slug'], status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Increment view count
        self.object.increment_views()
        
        # Get related posts
        context['related_posts'] = PortfolioService.get_related_blog_posts(self.object)
        
        # Get comments
        context['comments'] = self.object.comments.filter(
            is_approved=True,
            parent__isnull=True
        ).select_related('user')
        
        # Comment form
        context['comment_form'] = CommentForm()
        
        # SEO meta tags
        context['meta_tags'] = SEOService.get_meta_tags(self.object)
        
        # JSON-LD structured data
        context['structured_data'] = self.get_structured_data()
        
        AnalyticsService.track_visit(self.request, self.request.path)
        
        return context
    
    def get_structured_data(self):
        """Generate JSON-LD structured data for blog post"""
        data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": self.object.title,
            "description": self.object.excerpt,
            "author": {
                "@type": "Person",
                "name": self.object.author.get_full_name(),
            },
            "datePublished": self.object.published_at.isoformat(),
            "dateModified": self.object.updated_at.isoformat(),
        }
        return data


class ContactView(FormView):
    """Contact page with form"""
    template_name = 'portfolio/contact.html'
    form_class = ContactForm
    success_url = '/contact/success/'
    
    def form_valid(self, form):
        success, message = ContactService.save_contact_message(
            form.cleaned_data,
            self.request
        )
        
        if success:
            messages.success(self.request, 'Thank you! Your message has been sent successfully.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'An error occurred. Please try again later.')
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        AnalyticsService.track_visit(self.request, self.request.path)
        return context


class ContactSuccessView(TemplateView):
    """Contact form success page"""
    template_name = 'portfolio/contact_success.html'


class NewsletterSubscribeView(FormView):
    """Newsletter subscription view"""
    form_class = NewsletterForm
    http_method_names = ['post']
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        name = form.cleaned_data.get('name', '')
        
        success, subscriber = NewsletterService.subscribe(email, name)
        
        if success:
            messages.success(
                self.request,
                'Thanks for subscribing! Please check your email to confirm your subscription.'
            )
        else:
            messages.error(
                self.request,
                'Unable to subscribe. Please try again later.'
            )
        
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class AddCommentView(View):
    """Add comment to blog post"""
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        post_slug = self.kwargs.get('slug')
        post = get_object_or_404(BlogPost, slug=post_slug, status='published')

        form = CommentForm(request.POST)

        if form.is_valid():
            success, comment = CommentService.add_comment(
                post,
                form.cleaned_data,
                user=request.user if request.user.is_authenticated else None
            )

            if success:
                messages.success(request, 'Your comment has been submitted for moderation.')
            else:
                messages.error(request, 'Unable to post comment. Please try again.')
        else:
            messages.error(request, 'Unable to post comment. Please check your input and try again.')

        return redirect('portfolio:blog_detail', slug=post_slug)


class SearchView(TemplateView):
    """Global search results page"""
    template_name = 'portfolio/search_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', 'all')
        
        if query:
            results = PortfolioService.search_content(query, search_type if search_type != 'all' else None)
            context.update(results)
            context['query'] = query
            context['search_type'] = search_type
        
        return context


class SitemapView(TemplateView):
    """XML sitemap view"""
    template_name = 'portfolio/sitemap.xml'
    content_type = 'application/xml'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['urls'] = SEOService.generate_sitemap()
        return context


def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'portfolio/404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'portfolio/500.html', status=500)


def download_resume(request):
    """Download resume file"""
    import os
    from django.conf import settings
    from django.http import FileResponse, Http404
    
    resume_path = os.path.join(settings.MEDIA_ROOT, 'resume', 'resume.pdf')
    
    if os.path.exists(resume_path):
        response = FileResponse(open(resume_path, 'rb'))
        response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
        return response
    else:
        raise Http404("Resume not found")