from .models import Categorie
#adaug categoriile din Categorie in template-ul de baza
def categorii_context(request):
    return {
        "categorii": Categorie.objects.all()
    }
