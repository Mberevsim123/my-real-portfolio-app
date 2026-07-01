from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Projects
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/category/<slug:category_slug>/', views.ProjectListView.as_view(), name='project_category'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    
    # Blog
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/category/<slug:category_slug>/', views.BlogListView.as_view(), name='blog_category'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<slug:slug>/comment/', views.AddCommentView.as_view(), name='add_comment'),
    
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    
    # Resume
    path('resume/download/', views.download_resume, name='download_resume'),
    
    # Sitemap
    path('sitemap.xml/', views.SitemapView.as_view(), name='sitemap'),
]