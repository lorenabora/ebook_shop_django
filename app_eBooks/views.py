from django.shortcuts import render, get_object_or_404
from urllib.parse import urlparse

# Basic 
from django.http import HttpResponse
from .tracker import page_counter
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime
import time
import json

#####   MODELS  #####
from .models import Autor, Carte, Categorie, Vizualizari, Oferta, MyUser, Comanda
from .forms import FilterProducts, FormLogin, PromotieForm, ContactForm, save_message, Inregistrare, CarteForm
from django import forms
import uuid

#####   ERRORS    #####
from django.http import HttpResponseForbidden

#####   LINK TEMPLATES  #####
from django.db.models import Count
from django.shortcuts import render, redirect

##### LOGIN/OUT #####
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


#####   MAIL    #####
from django.core.mail import mail_admins
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings


log_access=[]
nr_access=0
access_log, access_info, access_main=0,0,0

def index(request):
    global access_main
    trimite_email()
    return render(request, "eBooks_Shop/index.html")
    #log_access.append(Accesare(request.META.get("REMOTE_ADDR"), request.path, datetime.now()))
    #access_main+=1
    # return HttpResponse("""
    #                  <html>
    #                  <body>
    #                  <b>Primul raspuns</b>
    #                  <p>Pentru iubitorii de lectura care isi doresc confortul de a purta asupra lor o poveste oriunde, oricum si oricand.</p>
    #                  <p>Acest site este destinat vanzarii de carti in format electronic( eBooks). In cateva minute dupa plasarea comenzii si finalizarea 
    #                  platii, clientii isi pot descarca pachetul pe orice dispozitiv, pentru o lectura in orice moment.<p>
    #                  </body>
    #                  </html>
    #                  """)   #aici vine descrierea pt mainpage
@login_required
def info(request):
    if not request.user.groups.filter(name="Administratori_site").exists():
        return interzis(request, titlu="Eroare acces info", mesaj="Nu ai voie să accesezi pagina info.")
    global access_info
    messages.debug(request, "Ai accesat pagina info.")
    parametri = request.GET
    data_html = afis_data(parametri.get("data")) if parametri.get("data") else ""
    return render(request, 'eBooks_Shop/info.html', {
        'parametri': parametri,
        'data_html': data_html,
    })
    # log_access.append(Accesare(request.META.get("REMOTE_ADDR"), request.path, datetime.now()))
    # access_info+=1
    # content=f"""<html>
    #                 <body>
    #                     <h1>Informatii despre server</h1>"""
    # if request.GET.get("data"):
    #     content+=f"<p>{afis_data(request.GET.get("data"))}</p>"
    # content+="<section><b>Parametrii</b></section>"
    # parametri=request.GET
    # content += f"<p>Număr de parametri: {len(parametri)}</p>"
    # content += "<ul>"
    # for nume in parametri:
    #     content += f"<li>{nume}</li>"
    # content += "</ul>"
    # content+="</body></html>"
    # return HttpResponse(content)
    

# def get_ip(request):
#     req_headers = request.META
#     str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
#     if str_lista_ip:
#         return str_lista_ip.split(',')[-1].strip()
#     else:
#         return request.META.get('REMOTE_ADDR')
    
def afis_data(data):
    zile = ['Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică']
    luni = ['Ianuarie', 'Februarie', 'Martie', 'Aprilie', 'Mai', 'Iunie',
            'Iulie', 'August', 'Septembrie', 'Octombrie', 'Noiembrie', 'Decembrie']
    dNow=datetime.now()
    sectiune="<section><b>Data si ora</b></section>"
    if data=="zi":
        sectiune+=f"<p>{zile[dNow.weekday()]}, {dNow.day} {luni[dNow.month - 1]} {dNow.year}</p>"
    elif data=="timp":
        sectiune+=f"<p>{dNow.strftime("%H:%M:%S")}</p>"
        # sectiune+=f"<p>{request.timestamp_str}</p>"
    return sectiune

# from urllib.parse import urlparse
class Accesare:
    _contor=0
    def __init__(self, ip_client, url, data):
        Accesare._contor+=1
        self.id= Accesare._contor
        self.ip_client=ip_client
        self.url=url
        self.data=data
    
    def __str__(self):
        return f"ID: {self.id}, IP: {self.ip_client}, URL: {self.url}, Data: {self.data.strftime('%Y-%m-%d %H:%M:%S')}"

    def lista_parametrii(self):
        lst=[]
        lst.append(("id", self.id) if self.id else ("id", None))
        lst.append(("ip_client", self.ip_client) if self.ip_client else ("ip_client", None))
        lst.append(("url", self.url) if self.url else ("url", None))
        lst.append(("data", self.data) if self.data else ("data", None))
        return lst
    
    def url(self):
        return self.url
    
    def data(self, stringF):
        return self.data.now().strftime(stringF)

    def pagina(self):
        # daca am parametri, exclud semnul intrebarii
        path = self.url.split("?")[0] if "?" in self.url else self.url
        if not path.startswith("/eBooks_Shop"):
            path="/"+path
        if path =="/" or path=="":
            return "/"
        # return path #imi da /eBooks_Shop/log....
        return "/" + path.split("/")[-1]
    
@login_required
def log(request):
    if not request.user.groups.filter(name="Administratori_site").exists():
        return interzis(request, titlu="Eroare acces log", mesaj="Nu ai voie să accesezi logul.")
    global access_log
    messages.debug(request, "Ai accesat pagina log.")
    # log_access.append(Accesare(request.META.get("REMOTE_ADDR"), request.path, datetime.now()))
    # access_log+=1
    ultimele = request.GET.get("ultimele") if request.GET.get("ultimele") else -1
    accesari= request.GET.get("accesari") if request.GET.get("accesari") else "nu"
    # iduri=request.GET.getlist("iduri")
    iduri=[]
    for id in request.GET.getlist("iduri"):
        iduri.extend(id.split(","))
    dubluri= True if request.GET.get("dubluri") else False
    # content="<html><body><h1>Log accesari</h1>"
    try:
        last=int(ultimele)
    except (TypeError, ValueError):
        return HttpResponse("<p>Parametrul 'ultimele' trebuie să fie un număr întreg.</p>")
    try:
        acc=str(accesari)
    except (TypeError, ValueError):
        return HttpResponse("<p>Parametrul 'accesari' trebuie sa fie de tip string</p>")
    accesari_list = []  #new update
    if last==-1:
        msg = ""
        pass
    else:
        if last<=len(log_access):
            for acc in log_access[:last]:
                # content+=f"<p>{acc}</p>"
                accesari_list = log_access[:last]
        else:
            accesari_list = log_access
            msg = f"Exista doar {len(log_access)} acccesari fata de {last} accesari cerute"
            # for l in log_access:
            #     content+=f"<p>{l}</p>"
            # content+=f"<p>Exista doar {len(log_access)} acccesari fata de {last} accesari cerute</p>"
    acc_info = {}
    if acc!="nu":
        #la accesari se va folosi middleware, toate paginile acelasi cod=>loc comun, preluare ip etc
        if acc=="nr":
            acc_info["nr"] = len(log_access)
            # content+=f"<p>Numarul de accesari in sesiunea curenta este: {len(log_access)}.</p>"
            if not dubluri:
                iduri = list(set(iduri)) 
            acc_info["iduri"] = iduri
            # content += "<p>ID-uri: " + ", ".join(str(id) for id in iduri) + ".</p>"
        elif acc=="detalii":
            # content+="<ul>"
            zile = ['Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică']
            luni = ['Ianuarie', 'Februarie', 'Martie', 'Aprilie', 'Mai', 'Iunie',
                    'Iulie', 'August', 'Septembrie', 'Octombrie', 'Noiembrie', 'Decembrie']
            acc_info["detalii"] = [
                f"{zile[a.data.weekday()]}, {a.data.day} {luni[a.data.month - 1]} {a.data.year}; {a.data.strftime('%H:%M:%S')}"
                for a in log_access
            ]
            # for a in log_access:
            #     dt = a.data
            #     zi = zile[dt.weekday()]
            #     luna = luni[dt.month - 1]
                # content += f"<li>{zi}, {dt.day} {luna} {dt.year}; {dt.strftime('%H:%M:%S')}</li>"
            # content+="</ul>"
    #tabel
    tabel=request.GET.get("tabel")
    table_data = []
    table_headers = []

    if tabel:
        fields = {
            "id": lambda a: a.id,
            "ip_client": lambda a: a.ip_client,
            "url": lambda a: a.url,
            "data": lambda acc: acc.data.strftime("%Y-%m-%d %H:%M:%S")
        }

        if tabel == "tot":
            show_fields = list(fields.keys())
        else:
            show_fields = [f for f in tabel.split(",") if f in fields]

        if show_fields:
            table_headers = show_fields
            for acc in log_access:
                row = [fields[f](acc) for f in show_fields]
                table_data.append(row)

        # if tabel=="tot":
        #     showTime=list(fields.keys())
        # else:
        #     showTime=tabel.split(",") if tabel else []
        #     showTime=[f for f in showTime if f in fields]
        # content+="<table border=1><tr>"
        # for title in showTime:
            # content+=f"<th>{title}</th>"
        # content+="</tr>"
        # for acc in log_access:
        #     content+="<tr>"
        #     for f in showTime:
        #         content+=f"<td>{fields[f](acc)}</td>"
        #     content+="</tr>"
        # content+="</table>"
        
    url_list=[acc.url for acc in log_access]
    url_counts = {path: url_list.count(path) for path in url_list}
    # most_visited = max(url_counts, key=url_counts.get)
    # least_visited = min(url_counts, key=url_counts.get)
    most_visited=max(page_counter, key=page_counter.get)
    least_visited=min(page_counter, key=page_counter.get)
    # content+=f"<p>Frecvent accesat: {most_visited}</p>"
    # content+=f"<p>Rar accesat: {least_visited}</p>"
    # content+="</body></html>"
    # return render(request, HttpResponse(content))
    return render(request, 'eBooks_Shop/log.html', {
        "accesari_list": accesari_list,
        "msg": msg if last != -1 and last > len(log_access) else "",
        "acc_info": acc_info,
        "table_headers": table_headers,
        "table_data": table_data,
        "most_visited": most_visited,
        "least_visited": least_visited
    })

# def afis_template(request):
#     return render(request,"eBooks_Shop/extensie.html",
#         {
#             "titlu_tab":"Titlu fereastra",
#             "titlu_articol":"Titlu afisat",
#             "continut_articol":"Continut text"
#         }
#     )
    
def afis_ext(request):
    return render(request,"eBooks_Shop/baza.html",
        {
            "param":"valoare parametru",
        }
    )
    
    
#######################     INCEPE ZONA DE PAGINI       #######################################    
    
def main_page(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    return render(request, "eBooks_Shop/main.html", {"client_ip": request.client_ip, "context":context})
    # return render(request, "eBooks_Shop/in_lucru.html", {"client_ip": request.client_ip})
def about(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    return render(request, "eBooks_Shop/about.html", {"client_ip": request.client_ip,"context":context})


######################      CARTE       ######################################################


def products(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    # return render(request, "eBooks_Shop/produse.html", {"client_ip": request.client_ip})
    sort = request.GET.get('sort')  # ia parametru din querystring
    form=FilterProducts(request.GET or None)
    produse=Carte.objects.all()
    items_per_pag=6 #default stabilit de mine
    repaginare=False
    if sort == 'a':
        produse = produse.order_by('titlu')
    elif sort == 'd': 
        produse = produse.order_by('-titlu')
        
    if form.is_valid():
        if form.cleaned_data.get('titlu'):
            produse=produse.filter(titlu__icontains=form.cleaned_data['titlu'])
        if form.cleaned_data.get('autor'):
            produse=produse.filter(autor__nume__icontains=form.cleaned_data['autor'])
        if form.cleaned_data.get('editura'):
            produse=produse.filter(id_editura__nume_editura__icontains=form.cleaned_data['editura'])
        if form.cleaned_data.get('pret_min'):
            produse=produse.filter(pret__gte=form.cleaned_data['pret_min'])
        if form.cleaned_data.get('pret_max'):
            produse=produse.filter(pret__lte=form.cleaned_data['pret_max'])
        if form.cleaned_data.get('data_publicarii'):
            produse=produse.filter(data_publicarii=form.cleaned_data['data_publicarii'])
        if form.cleaned_data.get('limba'):
            produse=produse.filter(limba__icontains=form.cleaned_data['limba'])
        if form.cleaned_data.get('format'):
            produse=produse.filter(format__icontains=form.cleaned_data['format'])
        if form.cleaned_data.get('spatiu_descarcare'):
            produse=produse.filter(spatiu_descarcare=form.cleaned_data['spatiu_descarcare'])
        if form.cleaned_data.get('in_stoc'):
            produse=produse.filter(in_stoc=True)
        if form.cleaned_data.get('categorii'):
            produse=produse.filter(categorii=form.cleaned_data['categorii'])
        if form.cleaned_data.get('oferte'):
            produse=produse.filter(oferte__discount__icontains=form.cleaned_data['oferte'])
        if form.cleaned_data.get('items_per_pag'):
            items_per_pag = int(form.cleaned_data['items_per_pag'])
            if items_per_pag != 6:
                repaginare = True
                messages.warning(request, "Atenție: în urma repaginării este posibil să fi sărit peste unele produse sau să revedeți produse deja vizualizate.")
        
    paginator = Paginator(produse, items_per_pag)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "eBooks_Shop/produse.html", 
                  {
                    "client_ip": request.client_ip,
                    "Carti": produse,
                    "form":form,
                    "page_obj": page_obj,
                    "repaginare":repaginare,
                    "context":context
                  })
    
def adauga_vizualizare(user, produs, N=5):
    Vizualizari.objects.create(utilizator=user, produs=produs)
    vizualizari = Vizualizari.objects.filter(utilizator=user).order_by("-data_vizualizare")#desc
    if vizualizari.count() > N:
        for v in vizualizari[N:]:
            v.delete()  
  
def detalii_autor(request, id_autor):
    autor = get_object_or_404(Autor, id_autor=id_autor)
    return render(request, "detalii_autor.html", {"autor": autor})

def detalii_oferta(request, id_oferta):
    oferta = get_object_or_404(Oferta, id_oferta=id_oferta)
    return render(request, "detalii_oferta.html", {"oferta": oferta})
              
def detalii_carte(request, id_carte):
    try:
        context = {
            "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
        }
        carte = get_object_or_404(Carte, id_carte=id_carte)
        if request.user.is_authenticated:
            adauga_vizualizare(request.user, carte, N=5)
        return render(request, "eBooks_Shop/detalii_carte.html", {'carte': carte,"client_ip": request.client_ip,"context":context})
    except Exception as e:
        #mail catre admini
        mail_admins(
            subject="Eroare la detalii_carte!",
            message=str(e),
            html_message=f"<div style='background-color:red; color:white; padding:10px;'>Eroare: {e}</div>"
        )
        return render(request, "eBooks_Shop/in_lucru.html", {"mesaj":"Ups! A aparut o eroare la afisarea detaliilor cartii..."})
        # return HttpResponse("A apărut o eroare, administratorii au fost notificați.")
        
def adauga_carte(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    if request.method == "POST":
        form = CarteForm(request.POST, request.FILES)
        if form.is_valid():
            # verific permisiuni
            if not request.user.has_perm("eBooks_Shop.add_carte"):
                # return interzis(request)
                messages.warning(request, "Nu ai voie să editezi acest câmp.")
                nume_produs=form.cleaned_data.get('titlu')
                accesari = request.session.get("ghinion_accesari", 0) + 1
                request.session["ghinion_accesari"] = accesari
                return HttpResponseForbidden(render(request, "eBooks_Shop/eroare_403.html",{
                    "client_ip":request.client_ip,
                    "titlu": "Eroare de adaugare produse",
                    "mesaj_personalizat": f"Nu ai voie să adaugi carti.",
                    "N_MAX_403": settings.N_MAX_403,
                    "ghinion_accesari": accesari,
                }))
            else:
                form.save()
                messages.success(request, "Cartea a fost adaugata cu succes!")
                return redirect("produse") #dupa adugare, back to all books
    else:
        form = CarteForm()
    return render(request, "eBooks_Shop/adauga_carte.html", {"form": form, "client_ip": request.client_ip,"context":context})


def detalii_categorie(request, nume_categorie):
    categorie = get_object_or_404(Categorie, nume=nume_categorie)
    form = FilterProducts(request.GET or None, initial={'categorie': categorie.nume})
    form.fields['categorii'].widget = forms.HiddenInput()  # ascund câmpul
    carti = Carte.objects.filter(categorii=categorie)

    if form.is_valid():
        cd = form.cleaned_data
        if cd.get('categorii') and cd['categorii'] != categorie.nume:
            messages.error(request, "Categoria selectată nu este validă.") #somehow user a modificat categoria
        else:
            carti = carti.filter(categorii__nume=categorie.nume)

    return render(request, "eBooks_shop/produse.html", {
        "client_ip": request.client_ip,
        'categorie': categorie,
        'page_obj': carti, 
        'form':form,
    })

# def contact(request):
#     # return render(request, "eBooks_Shop/contact.html", {"client_ip": request.client_ip})
#     return render(request, "eBooks_Shop/in_lucru.html", {"client_ip": request.client_ip})


######################      COS VIRTUAL     #############################################

def virtual_basket(request):
    return render(request, "eBooks_Shop/cos.html", {"client_ip": request.client_ip})
    # return render(request, "eBooks_Shop/in_lucru.html", {"client_ip": request.client_ip})

from django.http import JsonResponse

def produse_cos_json(request):
    ids = request.GET.get("ids", "")
    id_list = [i for i in ids.split(",") if i]

    produse = Carte.objects.filter(id_carte__in=id_list)
    data = {str(c.id_carte): {"imagine":c.imagine.url if c.imagine else "", "titlu": c.titlu, "pret": c.pret,"url": c.get_absolute_url()} for c in produse}
    return JsonResponse(data)

from .factura import send_factura_email, build_factura_pdf
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def cumpara(request): 
    if request.method != "POST": 
        return JsonResponse({"status": "error", "message": "Metodă neacceptată"}, status=405) 
    if not request.user.is_authenticated: 
        return JsonResponse({"status": "error", "message": "Autentificare necesară"}, status=401) 
    
    try: 
        payload = json.loads(request.body) 
    except json.JSONDecodeError: 
        return JsonResponse({"status": "error", "message": "JSON invalid"}, status=400) 
    
    cos = payload.get("cos", {}) 
    if not cos: 
        return JsonResponse({"status": "error", "message": "Coșul este gol"}, status=400) # Îmbogățire coș 
    
    produse_data = {} 
    for produs_id, qty in cos.items(): 
        try: 
            carte = Carte.objects.get(pk=produs_id) 
            url = carte.get_absolute_url() if hasattr(carte, "get_absolute_url") else f"/produse/{carte.pk}/" 
            produse_data[str(produs_id)] = { "titlu": carte.titlu, "cantitate": int(qty), "pret_unitar": float(carte.pret), "url": url, } 
        except Carte.DoesNotExist: 
            continue 
        
    comanda = Comanda.objects.create(utilizator=request.user, produse=produse_data) 
    try: 
        pdf_path = build_factura_pdf(comanda) 
        send_factura_email(comanda, pdf_path) 
    except Exception as e: 
        return JsonResponse({"status": "error", "message": f"Eroare la generarea sau trimiterea facturii: {e}"}, status=500) 
    return JsonResponse({"status": "success", "message": "Comanda a fost plasată, factura trimisă!", "id": comanda.id})

######################         REVIWS           ##########################################

def reviews(request):
    # return render(request, "eBooks_Shop/reviews.html", {"client_ip": request.client_ip})
    return render(request, "eBooks_Shop/in_lucru.html", {"client_ip": request.client_ip})


#######################     PROMOTII/OFERTE     ##########################################

def offerts(request):
    return render(request, "eBooks_Shop/in_lucru.html", {"client_ip":request.client_ip})

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission

@login_required
def activeaza_oferta(request):
    perm = Permission.objects.get(codename="vizualizeaza_oferta")
    request.user.user_permissions.add(perm)
    messages.success(request, "Ai primit permisiunea de vizualizare a ofertei!")
    return redirect("pagina_oferta")

@login_required
def pagina_oferta(request):
    messages.info(request, "Aceasta este oferta curentă.")
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    if not request.user.has_perm("eBooks_Shop.vizualizeaza_oferta"):
        return HttpResponseForbidden(render(request, "eBooks_Shop/eroare_403.html", {"titlu": "Eroare afisare oferta","mesaj": "Nu ai voie să vizualizezi oferta", "client_ip":request.client_ip}))
        # return HttpResponseForbidden("Nu ai permisiunea să vizualizezi oferta.")
    return render(request, "eBooks_Shop/oferta_noua.html", {"mesaj": "Reducere 50% la toate cărțile!", "client_ip":request.client_ip,"context":context})

def promotii(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    if request.method == "POST":
        form = PromotieForm(request.POST)
        if form.is_valid():
            promo = Oferta.objects.create(
                nume=form.cleaned_data["nume_promotie"],
                end_date=form.cleaned_data["timp_promotie"],
                discount=form.cleaned_data["discount_percent"],
                detalii=form.cleaned_data["mesaj"],
            )
            promo.categorii.set(form.cleaned_data["categorii"])
            # pragul minim vizualizari
            K = 3
            for categorie in form.cleaned_data["categorii"]:
                utilizatori = (
                    MyUser.objects
                    .filter(vizualizare__produs__categorie=categorie)
                    .annotate(num_viz=Count("vizualizare"))
                    .filter(num_viz__gte=K)
                )
                for user in utilizatori:
                    print(f"User eligibil: {user.email} pentru categoria {categorie.nume}")
                    promo.utilizatori.add(user)
            return redirect("trimite_promotii", oferta_id=promo.id_oferta)
    else:
        form = PromotieForm()
    return render(request, "eBooks_Shop/oferte.html", {"form": form,"context":context})
    # return render(request, "eBooks_Shop/in_lucru.html", {"client_ip": request.client_ip})


def contact(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():  
            nume = form.cleaned_data['nume']
            email = form.cleaned_data['email']
            mesaj = form.cleaned_data['mesaj']
            #procesarea datelor
            save_message(form.cleaned_data, request)
            messages.success(request, "Mesaj trimis cu succes!")
            return render(request, 'eBooks_Shop/contact.html', {'form': ContactForm()})
        else:
            print(form.errors)
    else:
        form = ContactForm()
    return render(request, 'eBooks_Shop/contact.html', {'form': form, "client_ip": request.client_ip,"context":context})


####################################        ZONA MAIL       ###############################################


def trimite_email(user):
    obj_site = Site.objects.get_current()
    domeniu = obj_site.domain
    url_imagine = f"http://{domeniu}{settings.STATIC_URL}app_eBooks/imagini/icon.png"
    confirm_link = f"http://localhost:8000/confirma_mail/{user.cod}/"
    html_message = render_to_string("email_confirmare.html", {
        "user": user,
        "confirm_link": confirm_link,
        "url_imagine": url_imagine
    })
    message = (
        f"Bun venit, {user.first_name} {user.last_name}!\n"
        f"Username-ul tău este: {user.username}\n"
        f"Confirmă emailul accesând: {confirm_link}"
    )
    send_mail(
        subject='Confirmare email',
        message=message,
        html_message=html_message,
        from_email='ebooks.shop1234567890@gmail.com',
        recipient_list=[{user.email}],
        fail_silently=False,
    )
    
def confirma_mail(request, cod):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    user = get_object_or_404(MyUser, cod=cod)
    user.email_confirmat = True
    user.save()
    return render(request, "eBooks_Shop/confirmare_succes.html", {"user": user, "client_ip": request.client_ip,"context":context})
   

def trimite_promotii_view(request, oferta_id):
    oferta = Oferta.objects.get(id_oferta=oferta_id)
    categorii = oferta.categorii.all()
    categorii_list = ", ".join([c.nume for c in categorii]) or "toate"
    ctx = {
        "subiect": oferta.nume or "Promoție specială",
        "end_date": oferta.end_date,
        "start_date":oferta.start_date,
        "discount": oferta.discount,
        "detalii": oferta.detalii or "Descoperă ofertele pe site.",
        "categorii": categorii_list,
        "url_promotie": f"http://localhost:8000/oferte/{oferta.id_oferta}/",
    }
    msg_new_comers = render_to_string("eBooks_Shop/oferta_new_comers.txt", ctx)
    msg_open_door = render_to_string("eBooks_Shop/oferta_open_doors.txt", ctx)
    subject = ctx["subiect"]
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "ebooks.shop1234567890@gmail.com")
    # lista de destinatari
    # destinatari = list(MyUser.objects.values_list("email", flat=True))
    destinatari = list(oferta.utilizatori.values_list("email", flat=True))
    # pregătim mesajele pentru send_mass_mail
    data = [
        (subject, msg_new_comers, from_email, destinatari),
        (subject, msg_open_door, from_email, destinatari),
    ]
    # trimit în masă
    send_mass_mail(data, fail_silently=False)
    return HttpResponse("Promoțiile au fost trimise!")


def trimite_mail_admini(request, time_window=200, username="", email=""):
    if time_window<120:
        mail_admins(
        subject="Logari suspecte",
        message=f"Username: {username}\nIP: {request.client_ip}",
        html_message=f"<h1 style='color:red'>Logari suspecte</h1><p>Username: {username}<br>IP: {request.client_ip}</p>"
    )
    if username.lower()=='admin':
        mail_admins(
            subject="cineva incearca sa ne preia site-ul",
            message=f"Atentie la IP: {request.client_ip}. Mail: {email}",
            html_message=f"<h1 style='color:red'>cineva incearca sa ne preia site-ul</h1><br>IP: {request.client_ip}. Mail: {email}</p>"
        )
    

##################################      ZONA LOGARE/INREGISTRARE        ##########################################


# failed=0
# first_failed=0
# last_failed=0
def login_view(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    # global failed, first_failed, last_failed
    failed = request.session.get("failed", 0) + 1
    request.session["failed"] = failed
    if request.method == 'POST':
        form = FormLogin(request.POST)
        form.request = request
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            # if username=='admin':
            #         trimite_mail_admini(request, username=username, email=email)
            #         return redirect('login')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # resetez contor
                request.session["failed"] = 0
                request.session["first_failed"] = 0
                if user.email_confirmat: #mail confirmat?
                    if user.blocat:  
                        return HttpResponseForbidden("Contul tău a fost blocat. Contactează administratorul.")
                    else:
                        login(request, user)
                    if remember_me:
                        request.session.set_expiry(60 * 60 * 24)  #1 zi
                    else:
                        request.session.set_expiry(0) 
                    messages.info(request, f"Bun venit, {username}!")
                    request.session['user_data'] = { "username": user.username, 
                                                    "email": user.email, 
                                                    "first_name": user.first_name, 
                                                    "last_name": user.last_name, 
                                                    "telefon": user.telefon, 
                                                    "adresa": user.adresa, 
                                                    "blocat": user.blocat, }
                    return redirect('contul_meu')  
                else:
                    form.add_error(None,"Pentru logare este necesar sa va confirmati mailul.")
            else:
                # #adaug logica pentru failed attemps
                # failed+=1
                # if failed==1:
                #     first_failed=int(time.time())
                # if failed>=3:
                #     last_failed=int(time.time())
                #     trimite_mail_admini(request, time_window=last_failed-first_failed, username=username)
                #     failed=0
                messages.error(request, "Ups! Datele nu au fost gasite.")
                form.add_error(None, "Username sau parolă incorecta.")
        else:
            #adaug logica pentru failed attemps
            failed+=1
            request.session["failed"] = failed
            if failed==1:
                # first_failed=int(time.time())
                request.session["first_failed"] = int(time.time())
            if failed>=3:
                last_failed=int(time.time())
                first_failed = request.session.get("first_failed", last_failed)
                trimite_mail_admini(request, time_window=last_failed-first_failed, username=username, email=email)
                # failed=0
                request.session["failed"] = 0 
            
    else:
        form = FormLogin()
    return render(request, "eBooks_Shop/login.html", {'form': form, "client_ip": request.client_ip,"context":context})

def logout_view(request):
    logout(request)
    request.user.user_permissions.clear()
    return redirect('login')  # redirect către pagina de login după logout

def contulMeu(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    user_data = request.session.get('user_data', {})
    return render(request, "eBooks_Shop/contul_meu.html", {"client_ip": request.client_ip,"context":context, "user_data": user_data})


def inregistrare_view(request):
    context = {
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    if request.method == "POST":
        form = Inregistrare(request.POST, request.FILES)
        if form.cleaned_data['username'].lower() == 'admin':
            trimite_mail_admini(request, username='admin', email=form.cleaned_data['email'])
            form.add_error("username", "Nu ai voie să îți alegi username 'admin'.")
            return render(request, "eBooks_Shop/inregistrare.html", {"form": form, "client_ip": request.client_ip})

        if form.is_valid():
            user = MyUser.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                telefon=form.cleaned_data["telefon"],
                data_nasterii=form.cleaned_data["data_nasterii"],
                adresa=form.cleaned_data["adresa"],
                avatar=form.cleaned_data["avatar"],
                bio=form.cleaned_data["bio"],
            )
            user.cod = str(uuid.uuid4())[:100] 
            user.save()
            trimite_email(user)
            return redirect("login")
    else:
        messages.error(request, "Ceva nu a mers bine, va rugam sa mai incercati o data.")
        form = Inregistrare()
    return render(request, "eBooks_Shop/inregistrare.html", {"form": form, "client_ip": request.client_ip,"context":context})

def interzis(request):
    accesari = request.session.get("ghinion_accesari", 0) + 1
    request.session["ghinion_accesari"] = accesari
    if accesari>N_MAX_403/2:
        messages.warning(request, "Ai ajuns de prea multe ori pe pagina interzisă!")
    context = {
        "titlu": "",
        "mesaj_personalizat": "Nu este permis accesul la resursa curentă.",
        "ghinion_accesari": accesari,
        "N_MAX_403": settings.N_MAX_403,
        "client_ip":request.client_ip,
        "is_admin_site": request.user.is_authenticated and request.user.groups.filter(name="Administratori_site").exists()
    }
    return render(request, "eBooks_Shop/eroare_403.html", context, status=403)




##########################################      MESAJE      #####################################################
from django.contrib import messages

def afisare(request):
    # Exemplu de mesaje
    messages.debug(request, "Acesta este un mesaj de depanare. :( ")
    messages.info(request, "Acesta este un mesaj informativ. :) ")
    messages.success(request, "Actiunea a avut succes! :D ")
    messages.warning(request, "Acesta este un avertisment. :| ")
    messages.error(request, "A aparut o eroare! >:((  ")
   
    return render(request, 'un_template.html')