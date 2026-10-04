import os
import time
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa

import random
import string

def random_serie():
    return ''.join(random.choices(string.ascii_uppercase, k=random.randint(2, 4)))

def random_numar():
    return str(random.randint(100000, 999999))


def build_factura_payload(comanda):
    produse_list = []
    total_cantitate = 0
    total_pret = 0.0

    for pid, data in comanda.produse.items():
        qty = int(data.get("cantitate", 0))
        pret = float(data.get("pret_unitar", 0))
        subtotal = qty * pret
        total_cantitate += qty
        total_pret += subtotal
        tva_unitar = pret * 0.05
        subtotal_tva = subtotal * 0.05
        produse_list.append({
            "id": pid,
            "titlu": data.get("titlu", ""),
            "cantitate": qty,
            "pret_unitar": pret,
            "tva_unitar": tva_unitar,
            "subtotal": subtotal+subtotal_tva,
            "url": data.get("url", f"/produse/{pid}/"),
        })
    admin_emails = ", ".join([email for _, email in settings.ADMINS])
    total_fara_tva = total_pret
    tva = round(total_fara_tva * 0.05, 2)  # TVA 5%
    total_cu_tva = round(total_fara_tva + tva, 2)
    return {
        "produse_list": produse_list,
        "total_cantitate": total_cantitate,
        "total_pret": total_pret,
        "total_fara_tva": total_fara_tva, 
        "tva": tva, 
        "total_cu_tva": total_cu_tva,
        "admin_email": admin_emails,
    }

def render_pdf_to_path(template_name, context, out_path):
    html = get_template(template_name).render(context)
    with open(out_path, "wb") as f:
        pisa_status = pisa.CreatePDF(html, dest=f)
    return (pisa_status.err == 0)

def build_factura_pdf(comanda):
    timestamp = int(time.time())
    user_folder = os.path.join(settings.MEDIA_ROOT, "temporar-facturi", comanda.utilizator.username)
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, f"factura-{timestamp}.pdf")
    icon_path = os.path.join(settings.BASE_DIR, "static", "imagini", "icon.png")
    ctx = {"comanda": comanda, 
           "serie": random_serie(), 
           "numar_factura": random_numar(),
           "data_factura": comanda.data, 
           "icon_path": icon_path,
           **build_factura_payload(comanda)}
    ok = render_pdf_to_path("eBooks_Shop/factura.html", ctx, file_path)
    if not ok:
        raise RuntimeError("Generarea PDF a eșuat")
    return file_path


from django.core.mail import EmailMessage
from django.conf import settings

def send_factura_email(comanda, pdf_path):
    email = EmailMessage(
        subject="Factura comanda",
        body="Atașat găsiți factura în format PDF. Vă mulțumim!",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "admin@site.com"),
        to=[comanda.utilizator.email],
    )
    email.attach_file(pdf_path)
    email.send()