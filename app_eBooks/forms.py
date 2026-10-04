from django import forms
from .models import Editura, Categorie, MyUser, Carte
from .validari import validare_capslock, validare_cnp, validare_email_temporal, validare_format_text, validare_major, validare_mesaj_cuvinte, validare_subiect, validare_tip_mesaj, validare_password, validare_telefon, validare_in_range, validare_val_poz
from datetime import date
import re

def calculeaza_varsta(data_nasterii):
    azi = date.today()
    ani = azi.year - data_nasterii.year
    luni = azi.month - data_nasterii.month
    if azi.day < data_nasterii.day:
        luni -= 1
    return f"{ani} ani și {luni} luni"

def normalizare_mesaj(msg):
    msg = msg.replace("\n", " ")
    msg = re.sub(r'\s+', ' ', msg)
    return msg.strip()

# def capitalize_after_punctuation(msg):
#     # regex: terminator + spațiu + literă mică
#     msg = re.sub(r'([.!?…]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), msg)
#     return msg
def capitalize_after_punctuation(msg):
    def repl(match):
        # group(1) = terminator + spațiu
        # group(2) = litera mică
        return match.group(1) + match.group(2).upper()
    msg = re.sub(r'([.!?…]\s+)([a-z])', repl, msg)
    return msg

OPTIUNI_MESAJ=(
    ('optiune1', 'neselectat'),
    ('optiune2', 'reclamatie'),
    ('optiune3', 'intrebare'),
    ('optiune4', 'review'),
    ('optiune5', 'cerere'),
    ('optiune6', 'programare')
)

class ContactForm(forms.Form):
    # nume = forms.CharField(max_length=100, label='Nume', required=True)
    nume = forms.CharField(
        max_length=10, required=True, label="Nume",
        validators=[validare_capslock, validare_format_text],
        error_messages={
            'required': 'Numele de utilizator este obligatoriu.',
            'max_length': 'Numele de utilizator nu poate depăși 10 caractere.'
        }
    )
    prenume=forms.CharField(max_length=10, required=False, label="Prenume", 
                            validators=[validare_format_text, validare_capslock])
    cnp=forms.CharField(min_length=13, max_length=13, label="CNP", required=False,
                        validators=[validare_cnp])
    data_nasterii=forms.DateField(label="Data nasterii", required=True,
                                  validators=[validare_major],
                                  widget=forms.DateInput(attrs={'type': 'date'}))
    # email = forms.EmailField(label='Email', required=True)
    email = forms.EmailField( label="Email", required=True,validators=[validare_email_temporal], 
        error_messages={
            'invalid': 'Introduceți o adresă de email validă.'
        }
    )
    confirm_email=forms.EmailField(label="Confirmare email", required=True, 
                                   error_messages={
                                        'invalid': 'Adresele trebuie sa coincida.'
                                    })
    tip_mesaj=forms.ChoiceField(label="Tip mesaj", required=True, choices=OPTIUNI_MESAJ, initial='optiune1',
                                validators=[validare_tip_mesaj])
    subiect=forms.CharField(label="Subiect", required=True, max_length=100,
                            validators=[validare_subiect, validare_format_text])
    minim_wait=forms.IntegerField(label="Pentru review-uri/cereri minimul de zile de asteptare trebuie setat de la 4 incolo iar pentru cereri/intrebari de la 2 incolo. Maximul e 30.",
                                  required=True)
    mesaj = forms.CharField(widget=forms.Textarea, label='Mesaj (semnați la final)', required=True,
                            validators=[validare_mesaj_cuvinte])
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@domeniu.com'):
            raise forms.ValidationError("Adresa de email trebuie să fie de la domeniu.com")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")
        tip = cleaned_data.get("tip_mesaj")
        min_wait = cleaned_data.get("minim_wait")
        mesaj = cleaned_data.get("mesaj")
        nume = cleaned_data.get("nume") 
        cnp = cleaned_data.get("cnp")
        data_nasterii = cleaned_data.get("data_nasterii")
        urgent = False
        if email and confirm_email and email != confirm_email:
            raise forms.ValidationError("Adresele de email nu coincid.")
        if tip in ["optiune4", "optiune5"] and min_wait < 4:
            raise forms.ValidationError("Pentru review-uri/cereri minimul este 4 zile.")
        if tip in ["optiune3", "optiune5"] and min_wait < 2:
            raise forms.ValidationError("Pentru întrebări/cereri minimul este 2 zile.")
        if min_wait and min_wait > 30:
            raise forms.ValidationError("Zilele de așteptare nu pot fi mai multe de 30.")
        if mesaj and nume:
            words = mesaj.strip().split()
            if not words or words[-1] != nume:
                raise forms.ValidationError("Mesajul trebuie să se încheie cu numele utilizatorului (semnătura).")
        if cnp and data_nasterii:
            an = int(cnp[1:3])
            luna = int(cnp[3:5])
            zi = int(cnp[5:7])
            if cnp[0] in ['1','2']:
                an += 1900
            elif cnp[0] in ['5','6']:
                year += 2000
            if data_nasterii.year != an or data_nasterii.month != luna or data_nasterii.day != zi:
                raise forms.ValidationError("CNP-ul nu corespunde cu data nașterii.")
        if data_nasterii:
            cleaned_data["varsta"] = calculeaza_varsta(data_nasterii)
            cleaned_data.pop("data_nasterii")  # salvez varsta, nu data
        if mesaj:
            mesaj = normalizare_mesaj(mesaj)
            mesaj = capitalize_after_punctuation(mesaj)
            cleaned_data["mesaj"] = mesaj
        if tip in ["optiune4", "optiune5"] and min_wait == 4:
            urgent = True
        elif tip in ["optiune3", "optiune5"] and min_wait == 2:
            urgent = True
        cleaned_data["urgent"] = urgent
        return cleaned_data

OPTIUNI_LIMBA=(
    ('optiune1', 'romana'),
    ('optiune2', 'engleza'),
    ('optiune3', 'franceza'),
    ('optiune4', 'japoneza'),
    ('optiune5', 'coreana'),
)        
class FilterProducts(forms.Form):
    titlu=forms.CharField(max_length=200, label="Titlu", required=False,
                          widget=forms.TextInput(attrs={'placeholder': 'Introduceți titlul'}))
    autor=forms.CharField(max_length=100, label="Autor", required=False)
    editura = forms.ModelChoiceField(
        queryset=Editura.objects.all(),
        required=False,
        label="Editura",
        widget=forms.Select()
    )
    pret_min = forms.DecimalField(required=False,initial =0, label="Preț minim", min_value=0,
                                   widget=forms.NumberInput(attrs={'placeholder': 'Min'}))
    pret_max = forms.DecimalField(required=False,initial=100, label="Preț maxim", max_value=100,
                                  widget=forms.NumberInput(attrs={'placeholder': 'Max'}))
    data_publicarii=forms.DateField(label="Data publicarii", required=False,
                                    widget=forms.DateInput(attrs={'type': 'date'}))
    limba=forms.ChoiceField(choices=OPTIUNI_LIMBA, label="Limba", required=False,
                             widget=forms.Select())
    format=forms.CharField(max_length=50, label="Format", required=False)
    spatiu_descarcare=forms.DecimalField(max_digits=6, decimal_places=2, label="Spatiu descarcare", required=False)
    in_stoc=forms.BooleanField(required=False, label="In stoc")
    # descriere=forms.CharField(max_length=255, label="Descriere", required=False)
    # categorii=forms.CharField(max_length=100, label="Categorii", required=False)
    categorii = forms.ModelChoiceField(queryset=Categorie.objects.all(),required=False,label="Categorie",
        widget=forms.Select())
    oferte=forms.CharField(max_length=255, label="Oferte", required=False)
    items_per_pag = forms.IntegerField(
        required=False,
        label="Produse afisate pe pagină"
    )
    
    def clean_titlu(self):
        titlu = self.cleaned_data.get('titlu')
        if titlu and len(titlu) < 2:
            raise forms.ValidationError("Titlul trebuie să aibă minim 2 caractere.")
        return titlu

    def clean_data_publicarii(self):
        data = self.cleaned_data.get('data_publicarii')
        if data and data.year < 1900:
            raise forms.ValidationError("Data publicării trebuie să fie după anul 1900.")
        return data

    def clean(self):
        cleaned_data = super().clean()
        pret_min = cleaned_data.get('pret_min')
        pret_max = cleaned_data.get('pret_max')
        if pret_min and pret_max and pret_min > pret_max and pret_min<0:
            raise forms.ValidationError("Prețul minim nu poate fi mai mare decât prețul maxim sau mai mic de 0.")
        return cleaned_data
    
    
import time, os, json
from django.conf import settings

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def save_message(cleaned_data, request):
    if "confirm_email" in cleaned_data:
        cleaned_data.pop("confirm_email")
    # adaug metadate despre utilizator
    cleaned_data["ip"] = get_client_ip(request)
    cleaned_data["received_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    # nume fișier
    timestamp = int(time.time())
    filename = f"mesaj_{timestamp}"
    if cleaned_data.get("urgent"):
        filename += "_urgent"
    filename += ".json"
    # folder Mesaje
    folder = os.path.join(settings.BASE_DIR, "app_eBooks", "Mesaje")
    os.makedirs(folder, exist_ok=True)
    # scriere JSON
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
        
        
class Inregistrare(forms.Form):
    username= forms.CharField(max_length=50, label="Username", required=True)
    password= forms.CharField(max_length=100, label="Parola", required=True, widget=forms.PasswordInput(),
                              validators=[validare_password])
    email= forms.EmailField( label="Email", required=True,validators=[validare_email_temporal], 
        error_messages={'invalid': 'Introduceți o adresă de email validă.'})
    first_name=forms.CharField(max_length=100, label="Prenume", required=True)
    last_name=forms.CharField(max_length=100, label="Nume", required=True)
    is_staff=forms.ChoiceField(choices=(('optiune1','nu'),('optiune2','da')), label="Staff", required=True)
    is_active=forms.ChoiceField(choices=(('optiune1','da'),('optiune2','nu')), label="Activ", required=False)
    date_joined=forms.DateField(label="Data inscrierii", required=False,
                                widget=forms.DateInput(attrs={'type': 'date'}))
    # last_login=forms.DateTimeField()
    telefon=forms.CharField(max_length=15, required=False, label="Telefon", validators=[validare_telefon])
    data_nasterii= forms.DateField(label="Data nasterii", required=True,
                                widget=forms.DateInput(attrs={'type': 'date'}), validators=[validare_major])
    adresa=forms.CharField(max_length=100, label="Adresa", required=False)
    gen= forms.ChoiceField(choices=(('optiune1', 'nu specific'), ('optiune2', 'femeie'), ('optiune3', 'barbat')), label='Gen', required=False)
    avatar=forms.ImageField(required=False, label="Avatar")
    bio=forms.CharField(max_length=500, label="Bio", required=False, validators=[validare_subiect])
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        if MyUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Acest username există deja. Alege altul.")
        return username

from django.contrib.auth import authenticate
class FormLogin(forms.Form):
    username = forms.CharField(max_length=50,label="Username",required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Introduceți username'}))
    email = forms.EmailField(label="Email",required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Introduceți email'}))
    password = forms.CharField(max_length=100,label="Parola",required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Introduceți parola'}))
    remember_me = forms.BooleanField(required=False, initial=False,label="Ține-mă minte pentru 1 zi")
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
    
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Username sau parola incorecta.")
        return self.cleaned_data
    
class PromotieForm(forms.Form):
    subiect = forms.CharField(max_length=150, label="Subiect")
    mesaj = forms.CharField(widget=forms.Textarea, label="Mesaj")
    nume_promotie = forms.CharField(max_length=150, label="Nume promoție")
    timp_promotie = forms.DateField(widget=forms.SelectDateWidget, label="Data expirării")
    categorii = forms.ModelMultipleChoiceField(
        queryset=Categorie.objects.none(),  # inițial gol
        widget=forms.CheckboxSelectMultiple,
        label="Categorii vizate"
    )
    discount_percent = forms.DecimalField(max_digits=5, decimal_places=2, label="Discount (%)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Categorie.objects.all()  # toate categoriile din DB
        self.fields["categorii"].queryset = qs
        self.fields["categorii"].initial = qs  # implicit toate selectate
        

#adaugam produse
class CarteForm(forms.ModelForm):
    #campuri aditionale: pret_baza+taxa_procent= pret_final (pe care il plateste utilizatorul la cumparare)
    pret_baza = forms.DecimalField(
        max_digits=5, decimal_places=2,
        label="Preț de bază",
        help_text="Introduceți prețul de bază al cărții.",
        validators=[validare_val_poz, validare_in_range]
    )
    taxa_procent = forms.IntegerField(
        label="Taxă procentuală",
        help_text="Introduceți procentul de taxă aplicat.",
        validators=[validare_val_poz]
    )
    class Meta:
        model = Carte
        fields = ["titlu", "descriere", "pret"]
        labels = {
            "titlu": "Titlul cărții( obligatoriu)",
            "descriere": "Descriere detaliată (short overview)",
        }
    def clean_titlu(self):
        titlu = self.cleaned_data.get("titlu")
        if len(titlu) < 2:
            raise forms.ValidationError("Titlul trebuie să aibă minim 2 caractere.")
        return titlu

    def clean_descriere(self):
        descriere = self.cleaned_data.get("descriere")
        if descriere and "fuck" in descriere.lower():
            raise forms.ValidationError("Descrierea nu poate conține cuvântul 'fuck'.")
        return descriere

    def clean_taxa_procent(self):
        taxa = self.cleaned_data.get("taxa_procent")
        if taxa > 50:
            raise forms.ValidationError("Taxa procentuală nu poate depăși 50%.")
        return taxa
    
    def clean(self):
        cleaned_data = super().clean()
        pret_baza = cleaned_data.get("pret_baza")
        taxa_procent = cleaned_data.get("taxa_procent")
        if pret_baza is not None and taxa_procent is not None:
            pret_final = pret_baza * (1 + taxa_procent / 100)
            if pret_final < pret_baza:
                raise forms.ValidationError("Prețul final calculat nu poate fi mai mic decât prețul de bază.")
        return cleaned_data
    
    # suprascriu save=>commit=False
    def save(self, commit=True):
        instance = super().save(commit=False)
        pret_baza = self.cleaned_data.get("pret_baza")
        taxa_procent = self.cleaned_data.get("taxa_procent")
        if pret_baza is not None and taxa_procent is not None:
            instance.pret = pret_baza * (1 + taxa_procent / 100)
        if commit:
            instance.save()
            self.save_m2m()  #pentru câmpurile ManyToMany 
        return instance