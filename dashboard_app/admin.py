from django.contrib import admin
from .models import BSDRegistro

@admin.register(BSDRegistro)
class BSDRegistroAdmin(admin.ModelAdmin):
    list_display = ('item', 'institucion', 'proyecto', 'monto_total', 'ejecutada')
    list_filter = ('ejecutada', 'vertice', 'proyecto')
    search_fields = ('institucion', 'proyecto')
