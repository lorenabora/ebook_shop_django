from django.core.exceptions import ValidationError
from datetime import date
import re
from datetime import date

def validare_major(data_nasterii):
    today=date.today()
    age= today.year-data_nasterii.year-((today.month,today.day)<(data_nasterii.month,data_nasterii.day))
    if age<18:
        raise ValidationError("Utilizatorul trebuie sa fie major.")
    
def validare_mesaj_cuvinte(mesaj):
    words=re.findall(r'\w+', mesaj)
    if len(words)<5 or len(words)>100:
        raise ValidationError("Mesajul trebuie sa contina intre 5 si 100 de cuvinte.")
    for wrd in words:
        if len(wrd)>15:
            raise ValidationError("Cuvintele nu pot depasi 15 litere.")
        if wrd.startswith("http://") or wrd.startswith("https://"):
            raise ValidationError("Mesajele nu pot contine linkuri.")
        
def validare_subiect(subj):
    words = subj.split()
    for w in words:
        if w.startswith("http://") or w.startswith("https://"):
            raise ValidationError("Subiectul nu poate conține linkuri.")
        
def validare_tip_mesaj(opt):
    if opt == 'optiune1': 
        raise ValidationError("Trebuie să selectați un tip de mesaj valid.")

def validare_cnp(cnp):
    if not cnp.isdigit():
        raise ValidationError("CNP-ul trebuie să conțină doar cifre.")
    if cnp[0] not in ['1', '2', '5', '6']: #am adaugat 5 si 6 pentru cei nascuti dupa anul 2000
        raise ValidationError("CNP-ul trebuie să înceapă cu 1 sau 2.")
    an = int(cnp[1:3])
    luna = int(cnp[3:5])
    zi = int(cnp[5:7])
    try:
        date(an + 1900, luna, zi)  # nu caut acum toti anii de la anul 0 si din 1900 se foloseste 1/2
    except ValueError:
        raise ValidationError("CNP-ul conține o dată invalidă.")
    
def validare_email_temporal(tmp):
    if tmp.endswith("guerillamail.com") or tmp.endswith("yopmail.com"):
        raise ValidationError("Nu sunt acceptate sdrese de mail temporale.")
    
def validare_format_text(txt):
    if not txt: 
        return
    if not re.match(r'^[A-Z][a-zA-Z\s-]*$', txt):
        raise ValidationError("Textul trebuie să înceapă cu literă mare și să conțină doar litere, spații sau cratime.")

def validare_capslock(txt):
    if not txt:
        return
    parts = re.split(r'[\s-]',txt )
    for p in parts:
        if p and not p[0].isupper():
            raise ValidationError("După spațiu sau cratimă trebuie să urmeze o literă mare.")
        
    
    
def validare_password(parola):
        # parola = psw.cleaned_data.get("password")
        if len(parola) < 10:
            raise ValidationError("Parola trebuie să aibă minim 10 caractere.")
        if not re.search(r"[A-Z]", parola):
            raise ValidationError("Parola trebuie să conțină cel puțin o literă mare.")
        if not re.search(r"[a-z]", parola):
            raise ValidationError("Parola trebuie să conțină cel puțin o literă mică.")
        if not re.search(r"\d", parola):
            raise ValidationError("Parola trebuie să conțină cel puțin o cifră.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", parola):
            raise ValidationError("Parola trebuie să conțină cel puțin un caracter special.")
        return parola

def validare_telefon(telefon):
    # telefon = telefon.cleaned_data.get("telefon")
    # adresa = adr.cleaned_data.get("adresa", "").lower()
    if telefon:
        if not re.match(r"^(\+40|0)\d{9}$", telefon):
                raise ValidationError("Telefon invalid pentru România (trebuie să înceapă cu +40 sau 0 și să aibă 10 cifre).")
    return telefon

def validare_user(value):
    no_go = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '\\', '/']
    for ch in value:
        if ch in no_go:
            raise ValidationError("Nume invalid, nu aveți voie să utilizați caractere speciale.")
    return value

def validare_val_poz(value):
    if value <= 0:
        raise ValidationError("Valoarea trebuie să fie pozitivă.")

def validare_in_range(value):
    if value > 200:
        raise ValidationError("Valoarea este prea mare (maxim 200).")

# def validare_data_nasterii(self):
#     from datetime import date
#     data = self.cleaned_data.get("data_nasterii")
#     if data:
#         azi = date.today()
#         varsta = azi.year - data.year - ((azi.month, azi.day) < (data.month, data.day))
#         if varsta < 18:
#                 raise ValidationError("Trebuie să aveți minim 18 ani pentru înregistrare.")
#     return data