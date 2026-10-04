from django.db import models
from datetime import datetime
import uuid
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
# class Locatie(models.Model):
#     adresa = models.CharField(max_length=255)
#     oras = models.CharField(max_length=100)
#     judet = models.CharField(max_length=100)
#     cod_postal = models.CharField(max_length=10)
    
#     def __str__(self):
#         return f"{self.adresa}, {self.oras}"

class Subcategorie(models.Model):
    id_subcategorie=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nume=models.CharField(max_length=200)
    popularitate=models.PositiveIntegerField()
    descriere=models.TextField(null=True)    #accepta valori nule
    
    def __str__(self):
        return f"{self.nume}, {self.popularitate}"

class Categorie(models.Model):
    id_categorie=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nume=models.CharField(max_length=255)
    descriere=models.TextField(null=True)    #permite null
    data_actualizarii=models.DateTimeField(auto_now=True)
    subcategorii = models.ManyToManyField(Subcategorie, blank=True)
    culoare = models.CharField(max_length=20, default="#37827c")
    icon = models.CharField(max_length=50, default="fa-tag")  # FontAwesome

    def __str__(self):
        return f"{self.nume}, {self.data_actualizarii}"
    def get_absolute_url(self):
        return reverse('detalii_categorie', kwargs={'nume_categorie': self.nume})

    

class Editura(models.Model):
    id_editura=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nume_editura= models.CharField(max_length=255)
    website=models.URLField(unique=True)   #camp unic
    adresa=models.CharField(max_length=500)
    mail= models.EmailField(unique=True)   #camp unic
    
    def __str__(self):
        return f"{self.nume_editura}"

OPTIUNI_LIMBA=(
    ('optiune1', 'romana'),
    ('optiune2', 'engleza'),
    ('optiune3', 'franceza'),
    ('optiune4', 'japoneza'),
    ('optiune5', 'coreana'),
)

class Autor(models.Model):
    id_autor= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nume= models.CharField(max_length=255)
    prenume=models.CharField(max_length=255)
    biografie= models.TextField()
    mail=models.EmailField(unique=True)    #camp unic
    
    def __str__(self):
        return f"{self.nume}, {self.prenume}"
    def get_absolute_url(self):
        return reverse('detalii_autor', kwargs={'id_autor': self.id_autor})

    #migrations ai 2 comenzi pt a introduce/actualiza bd-ul
    
from django.contrib.auth.models import AbstractUser
from django.db import models

class MyUser(AbstractUser):
    telefon = models.CharField(max_length=15, blank=True, null=True)
    data_nasterii = models.DateField(blank=True, null=True)
    adresa = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField()
    cod = models.CharField(max_length=100, blank=True, null=True) 
    email_confirmat = models.BooleanField(default=False)  
    blocat = models.BooleanField(default=False)
    
class Oferta(models.Model):
    id_oferta=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    nume=models.CharField(max_length=150, blank=True, null=True, default="")
    start_date=models.DateField(default=datetime.now())
    end_date=models.DateField()
    discount=models.DecimalField(max_digits=4, decimal_places=2)
    detalii=models.TextField()
    categorii = models.ManyToManyField(Categorie, related_name="oferte")
    utilizatori = models.ManyToManyField(MyUser, related_name="oferte_primite", blank=True)
    #adaugat pt oferta per categorie
    def __str__(self):
        return f"{self.start_date}, {self.end_date}, {self.discount}, {self.detalii}"
    def get_absolute_url(self):
        return reverse('detalii_oferta', kwargs={'id_oferta': self.id_oferta})
    class Meta:
        permissions = [
            ("vizualizeaza_oferta", "Poate vizualiza oferta specială"),
        ]
    
class Carte(models.Model):
    id_carte= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    titlu = models.CharField(max_length=255)
    autor = models.ManyToManyField(Autor)
    pret = models.DecimalField(max_digits=5, decimal_places=2)
    descriere = models.TextField()
    data_publicarii = models.DateField(default=datetime.now())    #data default a adaugarii?
    limba = models.CharField(max_length=100, choices=OPTIUNI_LIMBA)    #choice
    format = models.CharField(max_length=255, default='PDF')   #default pdf
    # path_file = models.FileField(upload_to='/')
    spatiu_descarcare = models.DecimalField(max_digits=6, decimal_places=2)
    in_stoc = models.BooleanField()
    id_editura =models.ForeignKey(Editura, to_field='id_editura', on_delete=models.CASCADE)
    categorii = models.ManyToManyField(Categorie, blank=True)
    oferte = models.ManyToManyField(Oferta, blank=True)
    stoc = models.IntegerField(default=0)
    
    imagine = models.ImageField(upload_to="carti/", blank=True, null=True)
    def __str__(self):
        return f"{self.titlu}, {self.pret}, {self.descriere}, {self.limba}, {self.format}, {self.in_stoc}"
    def get_absolute_url(self):
        return reverse('detalii_carte', kwargs={'id_carte': self.id_carte})
    
class Vizualizari(models.Model):
    id_vizualizare= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    utilizator = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    produs = models.ForeignKey(Carte, to_field="id_carte", on_delete=models.CASCADE)
    data_vizualizare = models.DateTimeField(auto_now_add=True)
    

class Comanda(models.Model):
    utilizator = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)
    produse = models.JSONField()  #ca in cos

    def __str__(self):
        return f"Comanda #{self.id} de la {self.utilizator.username}"
