from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from portfolio.sitemaps import BlogSitemap, ProjectSitemap, StaticSitemap


# ─── Patch ModelAdmin.Media to strip default CSS on every registered model ───
# Django injects CSS via ModelAdmin.Media in addition to base.html block stylesheets.
# Overriding it here means we don't have to touch every individual ModelAdmin class.
_original_media = admin.ModelAdmin.media.fget

def _stripped_media(self):
    original = _original_media(self)
    # Keep all JS (needed for widgets, actions, etc.) — drop only CSS
    original._css = {}
    return original

admin.ModelAdmin.media = property(_stripped_media)
# ─────────────────────────────────────────────────────────────────────────────


admin.site.site_header = '⬡ Portfolio Admin'
admin.site.site_title  = 'Portfolio Admin Panel'
admin.site.index_title = '✨ Welcome to Portfolio Management System'


sitemaps = {
    'static':   StaticSitemap,
    'projects': ProjectSitemap,
    'blog':     BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include('portfolio.api.urls')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(
         template_name='robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

handler404 = 'portfolio.views.handler404'
handler500 = 'portfolio.views.handler500'