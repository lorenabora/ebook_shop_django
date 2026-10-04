import schedule
import time
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from app_eBooks.models import MyUser, Subcategorie, Vizualizari
from django.core.mail import send_mail
from django.core.management import call_command
import os

logger = logging.getLogger(__name__)

#users neconfirmati bye
def sterge_utilizatori_neconfirmati():
    neconfirmati = MyUser.objects.filter(email_confirmat=False)
    for user in neconfirmati:
        logger.info(f"Sters utilizator neconfirmat: {user.username}")
        user.delete()

#newsletter saptamanal
def trimite_newsletter():
    limita = timezone.now()-timedelta(minutes=settings.OLD_X)
    utilizatori = MyUser.objects.filter(date_joined__lt=limita, email_confirmat=True)
    for user in utilizatori:
        continut = f"Salut {user.username}, recomandarea saptamanii: citeste o carte noua!"
        logger.info(f"Newsletter trimis catre {user.username}")
        send_mail(
            subject='Newsletter',
            message=continut,
            from_email='ebooks.shop1234567890@gmail.com',
            recipient_list=[{user.email}],
            fail_silently=False,
        )
        

#actualizare popularitate subcategorie
def actualizeaza_popularitate():
    for sub in Subcategorie.objects.all():
        vizualizari = Vizualizari.objects.filter(produs__categorii__subcategorii=sub).count()
        sub.popularitate = vizualizari
        sub.save()
        logger.info(f"Popularitate actualizata pentru {sub.nume}: {sub.popularitate}")

#backup zilnic
def backup_baza_date():
    logger.info("Backup automat al bazei de date efectuat.")
    # aici ai pune logica de dumpdata sau export DB
    data_str = timezone.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"backup_{data_str}.json")

    try:
        # rulează comanda dumpdata și scrie în fișier
        with open(backup_file, "w", encoding="utf-8") as f:
            call_command("dumpdata", "--natural-foreign", "--natural-primary", "--indent", "2", stdout=f)
        logger.info(f"Backup automat al bazei de date salvat în {backup_file}")
    except Exception as e:
        logger.error(f"Eroare la backup: {e}")


schedule.every(settings.K_MINUTE).minutes.do(sterge_utilizatori_neconfirmati)
zile_map = {
    "luni": schedule.every().monday,
    "marti": schedule.every().tuesday,
    "miercuri": schedule.every().wednesday,
    "joi": schedule.every().thursday,
    "vineri": schedule.every().friday,
    "sambata": schedule.every().saturday,
    "duminica": schedule.every().sunday,
}
zile_map[settings.ZI_SAPTAMANA_Z].at(f"{settings.ORA_O}:00").do(trimite_newsletter)
# schedule.every().monday.at(f"{settings.ORA_O}:00").do(trimite_newsletter)
schedule.every(settings.M_MINUTE).minutes.do(actualizeaza_popularitate)
zile_map[settings.Z2].at(f"{settings.O2}:00").do(backup_baza_date)
# schedule.every().thursday.at(f"{settings.O2}:00").do(backup_baza_date)


while True:
    schedule.run_pending()
    time.sleep(1)