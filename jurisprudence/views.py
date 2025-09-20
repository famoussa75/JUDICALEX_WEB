from datetime import date
from datetime import datetime, timedelta, date
from django.shortcuts import render
from .models import Jugement
from magistrats.models import Presidents
from django.core.paginator import Paginator
from start.models import Juridictions



# Create your views here.
def index(request):
   
    current_year = date.today().year
    year = int(request.GET.get('year', current_year))

    # Générer une liste d'années de 2010 à l'année courante
    available_years = list(range(2024, current_year + 1))

    today = datetime.today().strftime('%Y-%m-%d')
    jugements = Jugement.objects.all().order_by('-created_at')
    presidents = Presidents.objects.all().order_by('-created_at')
     # Nombre d'objets par page
    objets_par_page = 10

    paginator = Paginator(jugements, objets_par_page)

    # Récupérez le numéro de page à partir de la requête GET
    page_number = request.GET.get('page')
    
    # Obtenez les objets pour la page demandée
    jugements = paginator.get_page(page_number)

   
    juridictions = Juridictions.objects.all()
    query = []
    context = {
        'selected_year': year,
        'available_years': available_years,
        'jugements':jugements,
        'presidents':presidents,
        'juridictions':juridictions,
        'query':query,
        'today':today
    }
    
    return render(request, 'jurisprudence/jugements/index.html',context)