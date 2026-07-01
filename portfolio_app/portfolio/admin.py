from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Skill, Project, ProjectImage, BlogPost, Comment,
    ContactMessage, NewsletterSubscriber, Education, WorkExperience,
    Certification, SocialLink, SiteSetting, VisitorAnalytics
)
from django.contrib.admin import SimpleListFilter


class PublishedFilter(SimpleListFilter):
    """Custom filter for published content"""
    title = '📄 publication status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('published', '✅ Published'),
            ('draft', '📝 Draft'),
            ('archived', '📦 Archived'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'published':
            return queryset.filter(status='published')
        if self.value() == 'draft':
            return queryset.filter(status='draft')
        if self.value() == 'archived':
            return queryset.filter(status='archived')
        return queryset


class ProjectImageInline(admin.TabularInline):
    """Inline admin for project images"""
    model = ProjectImage
    extra = 1
    fields = ('image_preview', 'caption', 'order')
    readonly_fields = ('image_preview',)
    classes = ('collapse',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="border-radius: 8px; object-fit: cover;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for projects with modern design"""
    
    # FIXED: Added 'featured' to list_display (it was only in list_editable)
    list_display = ('image_preview', 'title', 'category', 'status_badge', 'featured', 'views_count', 'created_at', 'actions_display')
    list_filter = ('status', 'featured', 'category', PublishedFilter, 'created_at')
    search_fields = ('title', 'short_description', 'description', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('featured',)
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('title', 'slug', 'category', 'status', 'featured', 'featured_order')
        }),
        ('📝 Description', {
            'fields': ('short_description', 'description', 'technologies')
        }),
        ('🖼️ Media', {
            'fields': ('image', 'image_alt', 'video_url'),
            'classes': ('wide',)
        }),
        ('🔗 Links', {
            'fields': ('github_url', 'live_url', 'documentation_url')
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('📊 Statistics', {
            'fields': ('views_count', 'stars_count'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProjectImageInline]
    actions = ['publish_projects', 'unpublish_projects', 'feature_projects']
    
    readonly_fields = ('views_count', 'stars_count', 'created_at', 'updated_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'
    
    def status_badge(self, obj):
        colors = {
            'published': '#10b981',
            'draft': '#f59e0b',
            'archived': '#94a3b8'
        }
        icons = {
            'published': '✅',
            'draft': '📝',
            'archived': '📦'
        }
        color = colors.get(obj.status, '#94a3b8')
        icon = icons.get(obj.status, '📄')
        return mark_safe(f'<span style="background: {color}; color: white; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">{icon} {obj.get_status_display()}</span>')
    status_badge.short_description = 'Status'
    
    def actions_display(self, obj):
        url = reverse('admin:portfolio_project_change', args=[obj.pk])
        return mark_safe(f'''
        <a href="{url}" style="display: inline-block; padding: 4px 12px; background: #3b82f6; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 500;">✏️ Edit</a>
        ''')
    actions_display.short_description = 'Actions'
    
    def publish_projects(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'✅ {updated} projects published.')
    publish_projects.short_description = '📤 Publish selected projects'
    
    def unpublish_projects(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'📝 {updated} projects unpublished.')
    unpublish_projects.short_description = '📝 Unpublish selected projects'
    
    def feature_projects(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'⭐ {updated} projects featured.')
    feature_projects.short_description = '⭐ Feature selected projects'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Admin interface for blog posts with modern design"""
    
    # FIXED: Added 'status' to list_display (it was only in list_editable)
    list_display = ('title_preview', 'category', 'author', 'status', 'published_at', 'views_count', 'likes_count', 'actions_display')
    list_filter = ('status', 'category', 'author', 'published_at', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status',)
    list_per_page = 20
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('title', 'slug', 'category', 'status', 'author')
        }),
        ('📝 Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('🏷️ Metadata', {
            'fields': ('tags', 'read_time', 'allow_comments')
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('📊 Statistics', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        ('📅 Dates', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('views_count', 'likes_count', 'created_at', 'updated_at')
    actions = ['publish_posts', 'unpublish_posts']
    
    def title_preview(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_preview.short_description = 'Title'
    
    def actions_display(self, obj):
        url = reverse('admin:portfolio_blogpost_change', args=[obj.pk])
        return mark_safe(f'''
        <a href="{url}" style="display: inline-block; padding: 4px 12px; background: #3b82f6; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 500;">✏️ Edit</a>
        ''')
    actions_display.short_description = 'Actions'
    
    def publish_posts(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'✅ {updated} posts published.')
    publish_posts.short_description = '📤 Publish selected posts'
    
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'📝 {updated} posts unpublished.')
    unpublish_posts.short_description = '📝 Unpublish selected posts'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'projects_count', 'blog_posts_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    
    def projects_count(self, obj):
        return obj.projects.count()
    projects_count.short_description = '📁 Projects'
    
    def blog_posts_count(self, obj):
        return obj.blog_posts.count()
    blog_posts_count.short_description = '📝 Blog Posts'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    # FIXED: Added all editable fields to list_display
    list_display = ('name', 'category', 'proficiency', 'years_of_experience', 'order', 'is_active')
    list_filter = ('category', 'proficiency', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('proficiency', 'is_active', 'order')
    ordering = ('order', '-proficiency')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'full_subject', 'created_at', 'is_read', 'is_replied')
    list_filter = ('subject', 'is_read', 'is_replied', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'subject', 'custom_subject', 'message', 'ip_address', 'user_agent', 'created_at')
    actions = ['mark_as_read', 'mark_as_replied']
    list_per_page = 25
    
    def full_subject(self, obj):
        return obj.full_subject
    full_subject.short_description = 'Subject'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'✅ {updated} messages marked as read.')
    mark_as_read.short_description = '📨 Mark as read'
    
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(is_replied=True, replied_at=timezone.now())
        self.message_user(request, f'✉️ {updated} messages marked as replied.')
    mark_as_replied.short_description = '✉️ Mark as replied'
    
    def has_add_permission(self, request):
        return False


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'subscribed_at', 'is_active', 'is_confirmed')
    list_filter = ('is_active', 'is_confirmed', 'subscribed_at')
    search_fields = ('email', 'name')
    actions = ['activate_subscribers', 'deactivate_subscribers', 'export_emails']
    list_per_page = 25
    
    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ {updated} subscribers activated.')
    activate_subscribers.short_description = '🔓 Activate subscribers'
    
    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'🔒 {updated} subscribers deactivated.')
    deactivate_subscribers.short_description = '🔒 Deactivate subscribers'
    
    def export_emails(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Name', 'Subscribed Date', 'Status', 'Confirmed'])
        
        for subscriber in queryset:
            writer.writerow([subscriber.email, subscriber.name, subscriber.subscribed_at, subscriber.is_active, subscriber.is_confirmed])
        
        return response
    export_emails.short_description = '📥 Export emails to CSV'


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date')
    search_fields = ('degree', 'institution', 'field_of_study')
    ordering = ('-start_date',)


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date', 'company')
    search_fields = ('position', 'company', 'description')
    ordering = ('-start_date',)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuer', 'issue_date', 'expiry_date')
    list_filter = ('issuer', 'issue_date')
    search_fields = ('name', 'issuer', 'credential_id')


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('platform', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('platform', 'url')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    # FIXED: Added 'is_public' to list_display
    list_display = ('key', 'value_preview', 'is_public', 'description')
    search_fields = ('key', 'description')
    list_editable = ('is_public',)
    
    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'


@admin.register(VisitorAnalytics)
class VisitorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'page_url', 'visit_time', 'visit_duration', 'is_unique_visitor')
    list_filter = ('is_unique_visitor', 'visit_time')
    search_fields = ('session_id', 'page_url', 'referrer')
    readonly_fields = ('session_id', 'ip_address', 'user_agent', 'referrer', 'page_url', 'visit_time', 'is_unique_visitor')
    date_hierarchy = 'visit_time'
    list_per_page = 25
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'email', 'content')
    actions = ['approve_comments', 'disapprove_comments']
    list_per_page = 25
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'✅ {updated} comments approved.')
    approve_comments.short_description = '✅ Approve selected comments'
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'❌ {updated} comments disapproved.')
    disapprove_comments.short_description = '❌ Disapprove selected comments'


# Admin Site Customization
admin.site.site_header = '🚀 Portfolio Admin'
admin.site.site_title = 'Portfolio Admin Panel'
admin.site.index_title = '✨ Welcome to Portfolio Management System'