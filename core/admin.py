from django.contrib import admin
from unfold.admin import ModelAdmin  # Importa el ModelAdmin de Unfold
from .models import Order

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]  # Muestra todos los campos en la lista
    search_fields = ['id']  # Puedes personalizar los campos de búsqueda
    list_filter = []        # Puedes agregar filtros si lo deseas
    ordering = ['-id']     # Ordena por ID de forma descendente
    list_per_page = 10   # Número de elementos por página
    list_display_links = ['id']
    