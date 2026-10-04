"""
URL configuration for eBooks_Shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from app_eBooks.sitemaps import CarteSitemap, AutorSitemap, OfertaSitemap, StaticViewSitemap
from django.contrib.sitemaps import GenericSitemap
from app_eBooks.models import Categorie

# GenericSitemap pentru Categorie
categorie_info = {
    'queryset': Categorie.objects.all(),
    'date_field': 'data_actualizarii',
}
sitemap_categorii = GenericSitemap(categorie_info, priority=0.7)

sitemaps = {
    'carti': CarteSitemap,
    'autori': AutorSitemap,
    'oferte': OfertaSitemap,
    'categorii': sitemap_categorii,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),
    path('eBooks_Shop/', include("app_eBooks.urls")), #asta este la localhost
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
