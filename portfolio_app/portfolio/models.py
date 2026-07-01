from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator, URLValidator
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
from PIL import Image
import os

User = get_user_model()


class Category(models.Model):
    """Category for projects and blog posts"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    """Skills model with proficiency levels"""
    
    PROFICIENCY_LEVELS = [
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
        (5, 'Master'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='skills')
    proficiency = models.IntegerField(choices=PROFICIENCY_LEVELS, default=3)
    icon = models.CharField(max_length=100, blank=True, help_text="FontAwesome icon class")
    years_of_experience = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-proficiency', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-proficiency']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_proficiency_display()}"


class Project(models.Model):
    """Project portfolio model"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    technologies = models.TextField(help_text="Comma-separated list of technologies")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='projects')
    github_url = models.URLField(blank=True, validators=[URLValidator()])
    live_url = models.URLField(blank=True, validators=[URLValidator()])
    documentation_url = models.URLField(blank=True, validators=[URLValidator()])
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    image_alt = models.CharField(max_length=200, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    featured = models.BooleanField(default=False)
    featured_order = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField(default=0)
    stars_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=150, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-featured', '-featured_order', '-created_at']
        indexes = [
            models.Index(fields=['slug', 'status']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['featured', 'status']),
            models.Index(fields=['category', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        # Optimize image
        if self.image:
            self.optimize_image()
    
    def optimize_image(self):
        """Optimize project image for web"""
        img_path = self.image.path
        if os.path.exists(img_path):
            img = Image.open(img_path)
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            # Resize if too large
            max_size = (1200, 800)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            # Compress and save
            img.save(img_path, 'JPEG', quality=85, optimize=True)
    
    def get_technologies_list(self):
        """Return technologies as a list"""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    """Additional images for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.project.title}"


class BlogPost(models.Model):
    """Blog post model"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text="Short summary for blog listings")
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    tags = TaggableManager(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(default=timezone.now)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    read_time = models.PositiveIntegerField(default=5, help_text="Estimated read time in minutes")
    allow_comments = models.BooleanField(default=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=150, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['slug', 'status']),
            models.Index(fields=['-published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['author', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.read_time and self.content:
            # Calculate read time (average 200 words per minute)
            word_count = len(self.content.split())
            self.read_time = max(1, round(word_count / 200))
        super().save(*args, **kwargs)
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comments for blog posts"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"


class ContactMessage(models.Model):
    """Contact form messages"""
    
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('project', 'Project Collaboration'),
        ('job', 'Job Opportunity'),
        ('support', 'Technical Support'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    custom_subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    replied_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['email', 'is_read']),
        ]
    
    @property
    def full_subject(self):
        return self.custom_subject if self.custom_subject else dict(self.SUBJECT_CHOICES)[self.subject]
    
    def __str__(self):
        return f"Message from {self.name} - {self.full_subject}"


class NewsletterSubscriber(models.Model):
    """Newsletter subscribers"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.CharField(max_length=100, unique=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['-subscribed_at']),
        ]
    
    def __str__(self):
        return self.email


class Education(models.Model):
    """Education history"""
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
        verbose_name_plural = "Education"
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"


class WorkExperience(models.Model):
    """Work experience history"""
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    achievements = models.TextField(blank=True, help_text="Bullet points of key achievements")
    technologies = models.TextField(blank=True, help_text="Technologies used")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"
    
    def get_achievements_list(self):
        return [item.strip() for item in self.achievements.split('\n') if item.strip()]


class Certification(models.Model):
    """Professional certifications"""
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='certifications/', null=True, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return self.name


class SocialLink(models.Model):
    """Social media and professional links"""
    
    PLATFORM_CHOICES = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('medium', 'Medium'),
        ('devto', 'Dev.to'),
        ('stackoverflow', 'Stack Overflow'),
        ('reddit', 'Reddit'),
    ]
    
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    url = models.URLField()
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.get_platform_display()}"


class SiteSetting(models.Model):
    """Dynamic site settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    is_public = models.BooleanField(default=False, help_text="Whether this setting is exposed to templates")
    
    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return self.key


class VisitorAnalytics(models.Model):
    """Track visitor analytics"""
    session_id = models.CharField(max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField()
    referrer = models.URLField(blank=True)
    page_url = models.URLField()
    visit_time = models.DateTimeField(auto_now_add=True)
    visit_duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    is_unique_visitor = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['session_id', '-visit_time']),
            models.Index(fields=['visit_time']),
        ]
        verbose_name_plural = "Visitor Analytics"
    
    def __str__(self):
        return f"Visit at {self.visit_time}"
