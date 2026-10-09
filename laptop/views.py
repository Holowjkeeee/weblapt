from django.views.generic import TemplateView
from .models import Laptop

class ShowLaptopsView(TemplateView):
    template_name = "laptops/show_laptops.html"   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['laptops'] = Laptop.objects.all()
        return context