from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path("index", views.index, name="index"),
    path("info", views.info, name="info"),
    path("log", views.log, name="log"),
    # path("/extensie", views.afis_template, name="extensie1"),
    path("baza", views.afis_ext, name="baza"),
    path("", views.main_page, name="pagina_principala"),
    path("despre", views.about, name="despre"),
    path("categorii/<str:nume_categorie>/", views.detalii_categorie, name="detalii_categorie"),
    path("produse/<uuid:id_carte>/", views.detalii_carte, name="detalii_carte"),
    path("produse", views.products, name="produse"),
    path("adauga_carte/", views.adauga_carte, name="adauga_carte"),
    path("autor/<uuid:id_autor>/", views.detalii_autor, name="detalii_autor"),
    path("contact", views.contact, name="contact"),
    path("cos_virtual", views.virtual_basket, name="cos_virtual"),
    path("cos_virtual/api/cos-produse/", views.produse_cos_json, name="produse_cos_json"),
    path("cos_virtual/api/cumpara/", views.cumpara, name="cumpara"),
    path("recenzii", views.reviews, name="recenzii"),
    path("oferte/<uuid:id_oferta>/", views.detalii_oferta, name="detalii_oferta"),
    path("oferte", views.offerts, name="oferte"),
    path("promotii", views.promotii, name="promotii"),
    path("activeaza_oferta", views.activeaza_oferta, name="activeaza_oferta"),
    path("pagina_oferta", views.pagina_oferta, name="pagina_oferta"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("contul_meu", views.contulMeu, name="contul_meu"),
    path("schimba-parola/", auth_views.PasswordChangeView.as_view( template_name="eBooks_Shop/schimba_parola.html", success_url="/contul_meu/" ), name="schimba_parola"),
    path("sign_in", views.inregistrare_view, name="sign_in"),
    path("confirma_mail/<str:cod>/", views.confirma_mail, name="confirma_mail"),
    path("trimite_promotii/<uuid:id_oferta>/", views.trimite_promotii_view, name="trimite_promotii"),
    path("interzis", views.interzis, name="interzis")
]