from django.contrib import admin
# from .models import Locatie
from .models import Autor, Oferta, Editura, Carte, Subcategorie, Categorie, MyUser, Vizualizari
# Register your models here.
# admin.site.register(Locatie)
# admin.site.register(Autor)
# admin.site.register(Carte)
# admin.site.register(Categorie)
# admin.site.register(Subcategorie)
# admin.site.register(Oferta)
# admin.site.register(Editura)

admin.site.site_header = "eBooks_Shop Admin"
admin.site.site_title = "eBs Portal"
admin.site.index_title = "Bine ai venit în zona de administrare eBooks Shop"

class CarteAdmin(admin.ModelAdmin):
    list_display = ('titlu','get_autor', 'data_publicarii', 'get_editura')  # afișează câmpurile în lista de obiecte
    list_filter = ('titlu','autor__nume', 'data_publicarii', 'limba', 'format', 'pret', 'id_editura')  # adaugă filtre laterale
    search_fields = ('titlu', 'autor__nume')  # permite căutarea după anumite câmpuri
    filter_horizontal = ('autor',)
    ordering= ['-titlu', 'autor', 'pret']
    list_per_page=5
    fieldsets = (
        ('Informații Generale', {
            'fields': ('titlu', 'autor',  'pret','descriere', 'spatiu_descarcare', 'in_stoc', 'stoc')
        }),
        ('Date Publicare', {
            'fields': ('data_publicarii',),
            'classes': ('collapse',),
        }),
        ('Detalii', {
           'fields':('id_editura', 'limba', 'format', 'categorii', 'imagine', 'oferte') 
        }),
    )
    def get_autor(self, obj):
        return ", ".join([str(a) for a in obj.autor.all()]) # o carte poate avea mai multi autori
    get_autor.short_description = 'Autor'
    def get_editura(self, obj):
        return obj.id_editura.nume_editura
    get_editura.short_description='Editura'

    
admin.site.register(Carte, CarteAdmin)

class AutorAdmin(admin.ModelAdmin):
    search_fields=('prenume', 'nume')
    ordering=['-prenume']
    list_per_page=5
    

class EdituraAdmin(admin.ModelAdmin):
    search_fields=('nume_editura', 'website')
    

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nume', 'descriere', 'culoare', 'icon', 'data_actualizarii')
    # search_fields = ('nume',)
    search_fields=('nume', 'data_actualizarii')
    

class SubcategorieAdmin(admin.ModelAdmin):
    search_fields=('nume', 'popularitate')
    

class OfertaAdmin(admin.ModelAdmin):
    search_fields=('discount', 'end_date')
    
from django.contrib import admin
from .models import MyUser

@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "blocat")
    fields = ("first_name", "last_name", "email", "blocat") 

    
admin.site.register(Autor, AutorAdmin)
admin.site.register(Editura, EdituraAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Subcategorie, SubcategorieAdmin)
admin.site.register(Oferta, OfertaAdmin)
# admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Vizualizari)
# admin.site.register(MyUserAdmin)