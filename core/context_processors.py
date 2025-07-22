# core/context_processors.py

from .models import ServiceCategory

def homepage_categories(request):
    return {
        'homepage_categories': ServiceCategory.objects.filter(show_on_homepage=True)
    }
