"""
Business logic layer for portfolio app
"""

from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Avg
from .models import (
    Project, BlogPost, ContactMessage, NewsletterSubscriber,
    VisitorAnalytics, SiteSetting, Comment
)
from django.utils.crypto import get_random_string
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service class for portfolio operations"""
    
    @staticmethod
    def get_featured_projects(limit=3):
        """Get featured projects for homepage"""
        return Project.objects.filter(
            status='published',
            featured=True
        ).select_related('category')[:limit]
    
    @staticmethod
    def get_recent_blog_posts(limit=5):
        """Get recent published blog posts"""
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category')[:limit]
    
    @staticmethod
    def get_popular_projects(limit=4):
        """Get projects with highest views"""
        return Project.objects.filter(
            status='published'
        ).order_by('-views_count')[:limit]
    
    @staticmethod
    def get_trending_blog_posts(days=7, limit=4):
        """Get trending blog posts from last X days"""
        cutoff_date = timezone.now() - timedelta(days=days)
        return BlogPost.objects.filter(
            status='published',
            published_at__gte=cutoff_date
        ).order_by('-views_count', '-likes_count')[:limit]
    
    @staticmethod
    def search_content(query, model_type=None):
        """Global search across projects and blog posts"""
        results = {
            'projects': [],
            'blog_posts': [],
            'total_count': 0
        }
        
        if not query or len(query) < 2:
            return results
        
        # Search projects
        if not model_type or model_type == 'projects':
            results['projects'] = Project.objects.filter(
                Q(status='published'),
                Q(title__icontains=query) |
                Q(short_description__icontains=query) |
                Q(description__icontains=query) |
                Q(technologies__icontains=query)
            ).select_related('category')[:20]
        
        # Search blog posts
        if not model_type or model_type == 'blog':
            results['blog_posts'] = BlogPost.objects.filter(
                Q(status='published'),
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(content__icontains=query)
            ).select_related('author', 'category')[:20]
        
        results['total_count'] = len(results['projects']) + len(results['blog_posts'])
        
        return results
    
    @staticmethod
    def get_related_projects(project, limit=3):
        """Get related projects based on category and technologies"""
        project_techs = project.get_technologies_list()
        
        related = Project.objects.filter(
            status='published',
            category=project.category
        ).exclude(id=project.id)
        
        # Prioritize projects with similar technologies
        if project_techs:
            tech_queries = Q()
            for tech in project_techs[:3]:  # Limit to first 3 techs for performance
                tech_queries |= Q(technologies__icontains=tech)
            related = related.filter(tech_queries)
        
        return related[:limit]
    
    @staticmethod
    def get_related_blog_posts(blog_post, limit=3):
        """Get related blog posts based on category and tags"""
        related = BlogPost.objects.filter(
            status='published',
            category=blog_post.category
        ).exclude(id=blog_post.id)
        
        # Related by tags
        if blog_post.tags.exists():
            related = related.filter(tags__in=blog_post.tags.all()).distinct()
        
        return related[:limit]


class ContactService:
    """Service for handling contact messages"""
    
    @staticmethod
    def save_contact_message(data, request):
        """Save contact message and send notifications"""
        try:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Create message
            message = ContactMessage.objects.create(
                name=data['name'],
                email=data['email'],
                subject=data['subject'],
                custom_subject=data.get('custom_subject', ''),
                message=data['message'],
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            # Send notifications
            ContactService.send_admin_notification(message)
            ContactService.send_auto_reply(message)
            
            logger.info(f"Contact message received from {message.email}")
            return True, message
        
        except Exception as e:
            logger.error(f"Error saving contact message: {str(e)}")
            return False, None
    
    @staticmethod
    def send_admin_notification(message):
        """Send email notification to admin"""
        subject = f"New Contact Message: {message.full_subject}"
        html_content = render_to_string('portfolio/emails/admin_contact_notification.html', {
            'message': message,
            'admin_url': settings.SITE_URL + '/admin/portfolio/contactmessage/'
        })
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
            reply_to=[message.email]
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)
    
    @staticmethod
    def send_auto_reply(message):
        """Send auto-reply to user"""
        subject = "Thank you for contacting us"
        html_content = render_to_string('portfolio/emails/contact_auto_reply.html', {
            'name': message.name,
            'message': message
        })
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[message.email]
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)


class NewsletterService:
    """Service for newsletter operations"""
    
    @staticmethod
    def subscribe(email, name=''):
        """Subscribe a new user to newsletter"""
        try:
            # Check if already subscribed
            existing = NewsletterSubscriber.objects.filter(email=email).first()
            
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    existing.is_confirmed = False
                    existing.unsubscribed_at = None
                    existing.save()
                return True, existing
            else:
                # Create new subscription
                token = get_random_string(64)
                subscriber = NewsletterSubscriber.objects.create(
                    email=email,
                    name=name,
                    confirmation_token=token,
                    is_confirmed=False
                )
                
                # Send confirmation email
                NewsletterService.send_confirmation_email(subscriber)
                
                return True, subscriber
        
        except Exception as e:
            logger.error(f"Newsletter subscription error: {str(e)}")
            return False, None
    
    @staticmethod
    def confirm_subscription(token):
        """Confirm newsletter subscription"""
        try:
            subscriber = NewsletterSubscriber.objects.get(
                confirmation_token=token,
                is_confirmed=False
            )
            subscriber.is_confirmed = True
            subscriber.confirmation_token = ''
            subscriber.save()
            
            # Send welcome email
            NewsletterService.send_welcome_email(subscriber)
            
            return True, subscriber
        except NewsletterSubscriber.DoesNotExist:
            return False, None
    
    @staticmethod
    def unsubscribe(email):
        """Unsubscribe from newsletter"""
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email, is_active=True)
            subscriber.is_active = False
            subscriber.unsubscribed_at = timezone.now()
            subscriber.save()
            return True
        except NewsletterSubscriber.DoesNotExist:
            return False
    
    @staticmethod
    def send_confirmation_email(subscriber):
        """Send confirmation email to subscriber"""
        subject = "Confirm Your Newsletter Subscription"
        html_content = render_to_string('portfolio/emails/newsletter_confirmation.html', {
            'subscriber': subscriber,
            'confirm_url': f"{settings.SITE_URL}/newsletter/confirm/{subscriber.confirmation_token}/"
        })
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.email]
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)
    
    @staticmethod
    def send_welcome_email(subscriber):
        """Send welcome email to confirmed subscriber"""
        subject = "Welcome to Our Newsletter!"
        html_content = render_to_string('portfolio/emails/newsletter_welcome.html', {
            'subscriber': subscriber
        })
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.email]
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)


class AnalyticsService:
    """Service for tracking analytics"""
    
    @staticmethod
    def track_visit(request, page_url):
        """Track visitor analytics"""
        try:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            
            # Check if this is a unique visitor for today
            today = timezone.now().date()
            is_unique = not VisitorAnalytics.objects.filter(
                session_id=session_id,
                visit_time__date=today
            ).exists()
            
            VisitorAnalytics.objects.create(
                session_id=session_id,
                ip_address=AnalyticsService.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                referrer=request.META.get('HTTP_REFERER', ''),
                page_url=page_url,
                is_unique_visitor=is_unique
            )
            
            return True
        except Exception as e:
            logger.error(f"Analytics tracking error: {str(e)}")
            return False
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_statistics(days=30):
        """Get analytics statistics for dashboard"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        stats = {
            'total_visits': VisitorAnalytics.objects.filter(visit_time__gte=cutoff_date).count(),
            'unique_visitors': VisitorAnalytics.objects.filter(
                visit_time__gte=cutoff_date,
                is_unique_visitor=True
            ).values('session_id').distinct().count(),
            'most_viewed_pages': VisitorAnalytics.objects.filter(
                visit_time__gte=cutoff_date
            ).values('page_url').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        }
        
        return stats


class CommentService:
    """Service for handling comments"""
    
    @staticmethod
    def add_comment(blog_post, data, user=None):
        """Add a comment to a blog post"""
        try:
            comment = Comment.objects.create(
                post=blog_post,
                user=user,
                name=data['name'],
                email=data['email'],
                website=data.get('website', ''),
                content=data['content'],
                is_approved=False  # Requires moderation
            )
            
            # Notify admin about new comment
            CommentService.notify_admin(comment)
            
            logger.info(f"New comment added to post {blog_post.slug}")
            return True, comment
        
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            return False, None
    
    @staticmethod
    def notify_admin(comment):
        """Send notification to admin about new comment"""
        subject = f"New Comment on {comment.post.title}"
        html_content = render_to_string('portfolio/emails/new_comment_notification.html', {
            'comment': comment,
            'admin_url': settings.SITE_URL + '/admin/portfolio/comment/'
        })
        
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL]
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)


class SEOService:
    """Service for SEO optimization"""
    
    @staticmethod
    def generate_sitemap():
        """Generate XML sitemap"""
        from django.contrib.sitemaps import Sitemap
        from django.urls import reverse
        
        urls = []
        
        # Static pages
        static_pages = ['home', 'about', 'contact', 'projects', 'blog']
        for page in static_pages:
            urls.append({
                'url': reverse(f'portfolio:{page}'),
                'priority': 1.0 if page == 'home' else 0.8,
                'changefreq': 'weekly'
            })
        
        # Projects
        projects = Project.objects.filter(status='published')
        for project in projects:
            urls.append({
                'url': project.get_absolute_url(),
                'lastmod': project.updated_at,
                'priority': 0.9,
                'changefreq': 'monthly'
            })
        
        # Blog posts
        posts = BlogPost.objects.filter(status='published')
        for post in posts:
            urls.append({
                'url': post.get_absolute_url(),
                'lastmod': post.updated_at,
                'priority': 0.8,
                'changefreq': 'weekly'
            })
        
        return urls
    
    @staticmethod
    def get_meta_tags(obj):
        """Generate meta tags for an object"""
        meta = {
            'title': obj.meta_title or obj.title,
            'description': obj.meta_description or '',
            'keywords': obj.meta_keywords or '',
        }
        
        # Handle different object types
        if hasattr(obj, 'excerpt'):
            # BlogPost has excerpt
            if not meta['description']:
                meta['description'] = obj.excerpt[:160] if obj.excerpt else ''
        elif hasattr(obj, 'short_description'):
            # Project has short_description
            if not meta['description']:
                meta['description'] = obj.short_description[:160] if obj.short_description else ''
        elif hasattr(obj, 'description'):
            # Fallback to description
            if not meta['description']:
                meta['description'] = obj.description[:160] if obj.description else ''
        
        # Ensure description doesn't exceed 160 characters
        if meta['description'] and len(meta['description']) > 160:
            meta['description'] = meta['description'][:157] + '...'
        
        return meta