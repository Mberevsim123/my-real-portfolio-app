"""
Initialize the portfolio site with default data, superuser, and essential configurations.
Usage: python manage.py init_site
python manage.py init_site --demo
python manage.py init_site --force --email admin@example.com --password SecurePass123
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils.text import slugify
from django.utils import timezone
from portfolio.models import (
    Skill, Category, Education, WorkExperience, 
    SocialLink, SiteSetting, Project, BlogPost,
    Certification
)
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize the portfolio site with default data, superuser, and essential configurations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-initialization even if data exists',
        )
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Load demo data (projects, blog posts)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@portfolio.com',
            help='Superuser email address',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admin123!',
            help='Superuser password',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Starting portfolio site initialization...\n'))
        
        force = options['force']
        demo = options['demo']
        
        # Step 1: Create Superuser
        self.create_superuser(options['email'], options['password'])
        
        # Step 2: Create Default Categories
        categories = self.create_categories(force)
        
        # Step 3: Create Skills
        self.create_skills(categories, force)
        
        # Step 4: Create Social Links
        self.create_social_links(force)
        
        # Step 5: Create Site Settings
        self.create_site_settings(force)
        
        # Step 6: Create Work Experience
        self.create_work_experience(force)
        
        # Step 7: Create Education
        self.create_education(force)
        
        # Step 8: Create Certifications
        self.create_certifications(force)
        
        # Step 9: Load Demo Data (if requested)
        if demo:
            self.create_demo_projects(categories)
            self.create_demo_blog_posts()
            self.stdout.write(self.style.SUCCESS('✅ Demo data loaded successfully'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Portfolio site initialization completed successfully!\n'))
        self.stdout.write(self.style.WARNING('⚠️  Remember to update your .env file with production credentials!\n'))
    
    def create_superuser(self, email, password):
        """Create superuser if not exists"""
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email=email,
                username='admin',
                password=password,
                first_name='Admin',
                last_name='User',
                is_active=True,
                email_verified=True
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Superuser created: {email} / {password}'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Superuser already exists, skipping...'))
    
    def create_categories(self, force):
        """Create default categories"""
        categories_data = {
            'Backend Development': {
                'description': 'Backend development technologies and frameworks for building scalable APIs and services.',
                'icon': 'fas fa-server'
            },
            'Frontend Development': {
                'description': 'Frontend technologies and frameworks for building responsive user interfaces.',
                'icon': 'fas fa-desktop'
            },
            'DevOps': {
                'description': 'DevOps tools and practices for continuous integration and deployment.',
                'icon': 'fas fa-cloud-upload-alt'
            },
            'Database': {
                'description': 'Database technologies for data storage and management.',
                'icon': 'fas fa-database'
            },
            'Programming Languages': {
                'description': 'Programming languages for software development.',
                'icon': 'fas fa-code'
            },
            'Frameworks': {
                'description': 'Development frameworks and libraries.',
                'icon': 'fas fa-cubes'
            },
            'Cloud Services': {
                'description': 'Cloud platforms and services for scalable infrastructure.',
                'icon': 'fas fa-cloud'
            },
            'Tools': {
                'description': 'Development tools and utilities.',
                'icon': 'fas fa-tools'
            },
            'Security': {
                'description': 'Security practices and tools for secure applications.',
                'icon': 'fas fa-shield-alt'
            },
            'Testing': {
                'description': 'Testing frameworks and quality assurance tools.',
                'icon': 'fas fa-vial'
            }
        }
        
        categories = {}
        for name, data in categories_data.items():
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': data['description'],
                    'icon': data['icon']
                }
            )
            categories[name] = category
            if created:
                self.stdout.write(f'  ✓ Created category: {name}')
            elif force:
                category.description = data['description']
                category.icon = data['icon']
                category.save()
                self.stdout.write(f'  ✓ Updated category: {name}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {len(categories)} categories configured'))
        return categories
    
    def create_skills(self, categories, force):
        """Create default skills with proficiency levels"""
        skills_data = [
            # Programming Languages
            ('Python', 'Programming Languages', 5, 5, 'fab fa-python', 'High-level programming language for backend development'),
            ('JavaScript', 'Programming Languages', 4, 4, 'fab fa-js', 'Dynamic programming language for web development'),
            ('TypeScript', 'Programming Languages', 3, 2, 'fab fa-js', 'Typed JavaScript superset'),
            ('Go', 'Programming Languages', 3, 1, 'fab fa-golang', 'Efficient compiled language for backend'),
            
            # Frameworks
            ('Django', 'Frameworks', 5, 5, 'fab fa-python', 'High-level Python web framework'),
            ('Django REST Framework', 'Frameworks', 5, 4, 'fab fa-python', 'Powerful toolkit for building Web APIs'),
            ('FastAPI', 'Frameworks', 4, 2, 'fas fa-bolt', 'Modern Python web framework for APIs'),
            ('Flask', 'Frameworks', 4, 3, 'fas fa-flask', 'Micro web framework for Python'),
            
            # Database
            ('PostgreSQL', 'Database', 5, 5, 'fas fa-database', 'Advanced open-source relational database'),
            ('MySQL', 'Database', 4, 4, 'fas fa-database', 'Popular relational database management system'),
            ('MongoDB', 'Database', 3, 2, 'fas fa-database', 'NoSQL document database'),
            ('Redis', 'Database', 4, 3, 'fas fa-memory', 'In-memory data structure store'),
            
            # DevOps
            ('Docker', 'DevOps', 4, 4, 'fab fa-docker', 'Containerization platform'),
            ('Kubernetes', 'DevOps', 3, 2, 'fas fa-ship', 'Container orchestration platform'),
            ('AWS', 'Cloud Services', 4, 4, 'fab fa-aws', 'Amazon Web Services'),
            ('GitHub Actions', 'DevOps', 4, 3, 'fab fa-github', 'CI/CD automation platform'),
            
            # Tools
            ('Git', 'Tools', 5, 5, 'fab fa-git-alt', 'Distributed version control system'),
            ('Linux', 'Tools', 4, 5, 'fab fa-linux', 'Open-source operating system'),
            ('Postman', 'Tools', 4, 4, 'fas fa-paper-plane', 'API development and testing tool'),
            
            # Backend Development
            ('REST APIs', 'Backend Development', 5, 5, 'fas fa-plug', 'RESTful API design and development'),
            ('GraphQL', 'Backend Development', 3, 2, 'fas fa-chart-line', 'Query language for APIs'),
            ('WebSockets', 'Backend Development', 3, 1, 'fas fa-broadcast-tower', 'Real-time communication protocol'),
            
            # Security
            ('OAuth2', 'Security', 4, 3, 'fas fa-lock', 'Authorization framework'),
            ('JWT', 'Security', 4, 3, 'fas fa-key', 'JSON Web Tokens for authentication'),
            
            # Testing
            ('PyTest', 'Testing', 4, 4, 'fas fa-check-circle', 'Python testing framework'),
            ('UnitTest', 'Testing', 5, 5, 'fas fa-vial', 'Python built-in testing framework'),
        ]
        
        created_count = 0
        order = 0
        for name, category_name, proficiency, years, icon, description in skills_data:
            category = categories.get(category_name)
            if category:
                skill, created = Skill.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'proficiency': proficiency,
                        'years_of_experience': Decimal(str(years)),
                        'icon': icon,
                        'description': description,
                        'is_active': True,
                        'order': order
                    }
                )
                if created:
                    created_count += 1
                    order += 1
                    self.stdout.write(f'  ✓ Created skill: {name}')
                elif force:
                    skill.proficiency = proficiency
                    skill.years_of_experience = Decimal(str(years))
                    skill.description = description
                    skill.save()
                    self.stdout.write(f'  ✓ Updated skill: {name}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} skills configured'))
    
    def create_social_links(self, force):
        """Create social media links"""
        social_data = [
            ('github', 'https://github.com/yourusername', 'fab fa-github', 1, True),
            ('linkedin', 'https://linkedin.com/in/yourusername', 'fab fa-linkedin', 2, True),
            ('twitter', 'https://twitter.com/yourusername', 'fab fa-twitter', 3, True),
            ('stackoverflow', 'https://stackoverflow.com/users/youruserid', 'fab fa-stack-overflow', 4, False),
            ('medium', 'https://medium.com/@yourusername', 'fab fa-medium', 5, False),
        ]
        
        created_count = 0
        for platform, url, icon, order, is_active in social_data:
            link, created = SocialLink.objects.get_or_create(
                platform=platform,
                defaults={
                    'url': url,
                    'icon': icon,
                    'order': order,
                    'is_active': is_active
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created social link: {platform}')
            elif force:
                link.url = url
                link.save()
                self.stdout.write(f'  ✓ Updated social link: {platform}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} social links configured'))
    
    def create_site_settings(self, force):
        """Create site settings"""
        settings_data = [
            ('site_name', 'Backend Developer Portfolio', 'Site name displayed in header and meta tags', True),
            ('site_description', 'Professional backend developer portfolio showcasing projects, skills, and blog posts.', 'Site description for SEO', True),
            ('site_keywords', 'Django, Python, Backend Developer, Portfolio, Web Development, REST API', 'Site keywords for SEO', True),
            ('contact_email', 'contact@portfolio.com', 'Contact email address for inquiries', False),
            ('contact_phone', '+1 (555) 123-4567', 'Contact phone number', False),
            ('contact_address', 'San Francisco, CA', 'Physical address', False),
            ('resume_url', '/media/resume/resume.pdf', 'Resume file URL', False),
            ('github_username', 'yourusername', 'GitHub username for profile integration', False),
            ('twitter_username', '@yourusername', 'Twitter username for social media', False),
            ('linkedin_username', 'yourusername', 'LinkedIn username', False),
            ('google_analytics_id', '', 'Google Analytics tracking ID', False),
            ('recaptcha_site_key', '', 'Google reCAPTCHA site key', False),
            ('recaptcha_secret_key', '', 'Google reCAPTCHA secret key', False),
        ]
        
        created_count = 0
        for key, value, description, is_public in settings_data:
            setting, created = SiteSetting.objects.get_or_create(
                key=key,
                defaults={
                    'value': value,
                    'description': description,
                    'is_public': is_public
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created setting: {key}')
            elif force:
                setting.value = value
                setting.save()
                self.stdout.write(f'  ✓ Updated setting: {key}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} site settings configured'))
    
    def create_work_experience(self, force):
        """Create work experience entries"""
        experiences = [
            {
                'company': 'TechCorp Inc.',
                'position': 'Senior Backend Developer',
                'location': 'San Francisco, CA',
                'start_date': datetime(2022, 1, 1).date(),
                'is_current': True,
                'description': 'Leading backend development team for enterprise SaaS platform.',
                'achievements': '• Architected microservices architecture handling 100k+ requests/second\n• Improved API response time by 40% through caching and query optimization\n• Mentored 5 junior developers and conducted code reviews',
                'technologies': 'Django, PostgreSQL, Redis, Docker, AWS',
                'order': 1
            },
            {
                'company': 'StartUp Labs',
                'position': 'Backend Developer',
                'location': 'Austin, TX',
                'start_date': datetime(2019, 6, 1).date(),
                'end_date': datetime(2021, 12, 31).date(),
                'is_current': False,
                'description': 'Developed RESTful APIs and database schemas for e-commerce platform.',
                'achievements': '• Built payment integration system processing $1M+ monthly transactions\n• Reduced server costs by 25% through optimization\n• Implemented automated testing achieving 90% coverage',
                'technologies': 'Python, Django, PostgreSQL, Celery, Redis',
                'order': 2
            },
            {
                'company': 'Digital Agency',
                'position': 'Junior Developer',
                'location': 'Remote',
                'start_date': datetime(2018, 1, 1).date(),
                'end_date': datetime(2019, 5, 31).date(),
                'is_current': False,
                'description': 'Assisted in building web applications for various clients.',
                'achievements': '• Developed 10+ client websites and web applications\n• Created reusable component library reducing development time by 30%\n• Provided technical support and maintenance',
                'technologies': 'Python, Django, JavaScript, HTML/CSS',
                'order': 3
            }
        ]
        
        created_count = 0
        for exp_data in experiences:
            experience, created = WorkExperience.objects.get_or_create(
                company=exp_data['company'],
                position=exp_data['position'],
                defaults=exp_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created work experience: {exp_data["position"]} at {exp_data["company"]}')
            elif force:
                for key, value in exp_data.items():
                    setattr(experience, key, value)
                experience.save()
                self.stdout.write(f'  ✓ Updated work experience: {exp_data["position"]}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} work experiences configured'))
    
    def create_education(self, force):
        """Create education entries"""
        education_data = [
            {
                'institution': 'Stanford University',
                'degree': 'Master of Science',
                'field_of_study': 'Computer Science',
                'start_date': datetime(2016, 9, 1).date(),
                'end_date': datetime(2018, 6, 15).date(),
                'grade': '3.8 GPA',
                'description': 'Specialized in distributed systems and cloud computing. Thesis on microservices architecture.',
                'order': 1
            },
            {
                'institution': 'University of California, Berkeley',
                'degree': 'Bachelor of Science',
                'field_of_study': 'Computer Science',
                'start_date': datetime(2012, 9, 1).date(),
                'end_date': datetime(2016, 5, 15).date(),
                'grade': '3.6 GPA',
                'description': 'Relevant coursework: Data Structures, Algorithms, Database Systems, Web Development.',
                'order': 2
            }
        ]
        
        created_count = 0
        for edu_data in education_data:
            education, created = Education.objects.get_or_create(
                institution=edu_data['institution'],
                degree=edu_data['degree'],
                defaults=edu_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created education: {edu_data["degree"]} from {edu_data["institution"]}')
            elif force:
                for key, value in edu_data.items():
                    setattr(education, key, value)
                education.save()
                self.stdout.write(f'  ✓ Updated education: {edu_data["degree"]}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} education entries configured'))
    
    def create_certifications(self, force):
        """Create certification entries"""
        certifications_data = [
            {
                'name': 'AWS Solutions Architect',
                'issuer': 'Amazon Web Services',
                'issue_date': datetime(2023, 3, 15).date(),
                'expiry_date': datetime(2026, 3, 15).date(),
                'credential_id': 'AWS-12345',
                'credential_url': 'https://aws.amazon.com/verification',
                'order': 1
            },
            {
                'name': 'Django Professional Certification',
                'issuer': 'Django Software Foundation',
                'issue_date': datetime(2022, 8, 10).date(),
                'credential_id': 'DJANGO-67890',
                'credential_url': 'https://djangoproject.com/certification',
                'order': 2
            },
            {
                'name': 'Google Cloud Professional Developer',
                'issuer': 'Google Cloud',
                'issue_date': datetime(2023, 1, 20).date(),
                'expiry_date': datetime(2025, 1, 20).date(),
                'credential_id': 'GCP-54321',
                'order': 3
            }
        ]
        
        created_count = 0
        for cert_data in certifications_data:
            certification, created = Certification.objects.get_or_create(
                name=cert_data['name'],
                issuer=cert_data['issuer'],
                defaults=cert_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created certification: {cert_data["name"]}')
            elif force:
                for key, value in cert_data.items():
                    setattr(certification, key, value)
                certification.save()
                self.stdout.write(f'  ✓ Updated certification: {cert_data["name"]}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} certifications configured'))
    
    def create_demo_projects(self, categories):
        """Create demo projects for portfolio"""
        projects_data = [
            {
                'title': 'E-Commerce API Platform',
                'slug': 'ecommerce-api-platform',
                'short_description': 'High-performance REST API for e-commerce platform handling 100k+ requests/second.',
                'description': 'Built a scalable e-commerce API with Django REST Framework, PostgreSQL, and Redis caching. Features include user authentication, product management, shopping cart, order processing, payment integration with Stripe, and real-time inventory management.',
                'technologies': 'Django, DRF, PostgreSQL, Redis, Celery, Stripe API, Docker, AWS',
                'category': categories.get('Backend Development'),
                'github_url': 'https://github.com/yourusername/ecommerce-api',
                'live_url': 'https://api.yourdomain.com',
                'featured': True,
                'featured_order': 1,
                'status': 'published',
                'views_count': 1500,
            },
            {
                'title': 'Task Management System',
                'slug': 'task-management-system',
                'short_description': 'Project management tool with real-time updates and team collaboration features.',
                'description': 'Developed a full-featured task management system with WebSocket real-time updates, Kanban boards, team collaboration, file attachments, and activity logging. Includes JWT authentication, role-based permissions, and email notifications.',
                'technologies': 'Django, Channels, WebSockets, PostgreSQL, Redis, Bootstrap, JavaScript',
                'category': categories.get('Backend Development'),
                'github_url': 'https://github.com/yourusername/task-manager',
                'featured': True,
                'featured_order': 2,
                'status': 'published',
                'views_count': 980,
            },
            {
                'title': 'Blog Platform with AI Recommendations',
                'slug': 'blog-platform-ai',
                'short_description': 'Content management system with AI-powered content recommendations.',
                'description': 'Built a blog platform with custom CMS, SEO optimization, and machine learning-based content recommendations. Features include rich text editor, tag system, comment moderation, and analytics dashboard.',
                'technologies': 'Django, PostgreSQL, Elasticsearch, Redis, Celery, Scikit-learn, Bootstrap',
                'category': categories.get('Frameworks'),
                'github_url': 'https://github.com/yourusername/blog-platform',
                'live_url': 'https://blog.yourdomain.com',
                'featured': True,
                'featured_order': 3,
                'status': 'published',
                'views_count': 2100,
            },
            {
                'title': 'Social Media Analytics Dashboard',
                'slug': 'social-media-analytics',
                'short_description': 'Analytics dashboard for social media metrics and engagement tracking.',
                'description': 'Created an analytics dashboard that aggregates data from multiple social media APIs (Twitter, Facebook, Instagram). Features include real-time metrics, custom reports, data visualization charts, and export functionality.',
                'technologies': 'Django, Celery, Redis, Chart.js, Twitter API, Facebook Graph API, PostgreSQL',
                'category': categories.get('Cloud Services'),
                'github_url': 'https://github.com/yourusername/social-analytics',
                'status': 'published',
                'views_count': 750,
            },
            {
                'title': 'REST API Boilerplate',
                'slug': 'rest-api-boilerplate',
                'short_description': 'Production-ready REST API boilerplate with best practices.',
                'description': 'Comprehensive REST API boilerplate with JWT authentication, rate limiting, API versioning, Swagger documentation, testing setup, Docker configuration, and CI/CD pipeline.',
                'technologies': 'Django, DRF, JWT, Swagger, Docker, GitHub Actions, PostgreSQL, Redis',
                'category': categories.get('Backend Development'),
                'github_url': 'https://github.com/yourusername/api-boilerplate',
                'featured': False,
                'status': 'published',
                'views_count': 1200,
            },
            {
                'title': 'Real-time Chat Application',
                'slug': 'realtime-chat-app',
                'short_description': 'Scalable chat application with private rooms and file sharing.',
                'description': 'Built a real-time chat application using Django Channels and WebSockets. Features include private messaging, group chats, file attachments, emoji support, online status indicators, and message history.',
                'technologies': 'Django, Channels, WebSockets, Redis, PostgreSQL, Bootstrap',
                'category': categories.get('Backend Development'),
                'github_url': 'https://github.com/yourusername/chat-app',
                'status': 'published',
                'views_count': 890,
            }
        ]
        
        created_count = 0
        for proj_data in projects_data:
            project, created = Project.objects.get_or_create(
                slug=proj_data['slug'],
                defaults=proj_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created demo project: {proj_data["title"]}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} demo projects created'))
    
    def create_demo_blog_posts(self):
        """Create demo blog posts"""
        author = User.objects.filter(is_superuser=True).first()
        if not author:
            author = User.objects.create_user(
                email='author@portfolio.com',
                username='blog_author',
                password='Author123!',
                first_name='Blog',
                last_name='Author'
            )
        
        posts_data = [
            {
                'title': 'Building Scalable APIs with Django REST Framework',
                'slug': 'building-scalable-apis-django-rest-framework',
                'excerpt': 'Learn how to build high-performance REST APIs with Django REST Framework that can handle millions of requests.',
                'content': """# Building Scalable APIs with Django REST Framework

Django REST Framework (DRF) is a powerful toolkit for building Web APIs in Django. In this post, I'll share best practices for building scalable APIs.

## Key Optimizations

### Database Optimization
- Use `select_related` and `prefetch_related` to reduce queries
- Add appropriate database indexes
- Implement query optimization techniques

### Caching Strategy
- Implement Redis caching for frequently accessed data
- Use cache invalidation strategies
- Cache API responses when appropriate

### Pagination
- Always paginate list endpoints
- Use cursor-based pagination for large datasets
- Provide consistent pagination metadata

### Rate Limiting
- Implement rate limiting to prevent abuse
- Use different limits for authenticated vs anonymous users
- Return appropriate rate limit headers

## Example Implementation

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache

class ProductViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle]
    
    def list(self, request):
        cache_key = f'products_{request.user.id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        # ... fetch and return data
```""",
                'category': Category.objects.filter(name='Backend Development').first(),
                'author': author,
                'status': 'published',
                'published_at': timezone.now() - timedelta(days=5),
                'views_count': 450,
                'read_time': 8,
                'allow_comments': True,
            },
            {
                'title': 'Mastering PostgreSQL for Django Applications',
                'slug': 'mastering-postgresql-django-applications',
                'excerpt': 'Advanced PostgreSQL techniques to supercharge your Django applications.',
                'content': """# Mastering PostgreSQL for Django Applications

PostgreSQL is the recommended database for Django applications. Here are advanced techniques to optimize performance.

## Key Features

### Full-Text Search
Django provides full integration with PostgreSQL's full-text search capabilities.

### Indexing Strategies
- GIN indexes for array and full-text search
- B-tree indexes for frequent lookups
- Partial indexes for filtered queries

### JSON Field Usage
PostgreSQL's JSON fields allow flexible data storage.

### Connection Pooling
Use PgBouncer for connection pooling in production.""",
                'category': Category.objects.filter(name='Database').first(),
                'author': author,
                'status': 'published',
                'published_at': timezone.now() - timedelta(days=12),
                'views_count': 320,
                'read_time': 10,
                'allow_comments': True,
            },
            {
                'title': 'Dockerizing Django Applications for Production',
                'slug': 'dockerizing-django-production',
                'excerpt': 'Step-by-step guide to containerize Django applications with Docker for production deployment.',
                'content': """# Dockerizing Django Applications for Production

Docker has revolutionized how we deploy applications. Here's how to properly containerize Django for production.

## Multi-stage Dockerfile

```dockerfile
# Build stage
FROM python:3.12 as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["gunicorn", "config.wsgi:application"]