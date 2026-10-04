from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Carte, Autor, Oferta

class CarteSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Carte.objects.all()

    def location(self, obj):
        return f"/carte/{obj.id_carte}/"

class AutorSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Autor.objects.all()

    def location(self, obj):
        return f"/autor/{obj.id_autor}/"

class OfertaSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Oferta.objects.all()

    def location(self, obj):
        return f"/oferta/{obj.id_oferta}/"

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "yearly"

    def items(self):
        return ['main_page', 'contact', 'about']

    def location(self, item):
        return reverse(item)
