from django.db import models

class BSDRegistro(models.Model):
    ESTADO_CHOICES = [
        ('EJECUTADA', 'Ejecutada'),
        ('EN EJECUCION', 'En Ejecución'),
        ('POR DOTAR', 'Por Dotar'),
    ]
    
    VERTICE_CHOICES = [
        ('V1', 'V1'),
        ('V3', 'V3'),
        ('V4', 'V4'),
    ]
    
    item = models.IntegerField(verbose_name="Item")
    institucion = models.CharField(max_length=500, verbose_name="Institución")
    proyecto = models.CharField(max_length=100, verbose_name="Proyecto", blank=True, null=True)
    cant_articulos_dotados = models.IntegerField(verbose_name="Cant. Artículos Dotados", default=0)
    cant_articulos_faltantes = models.IntegerField(verbose_name="Cant. Artículos Faltantes", default=0)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Monto Total")
    monto_total_cobrado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Monto Total Cobrado", blank=True, null=True)
    monto_total_pendiente = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Monto Total Pendiente", blank=True, null=True)
    vertice = models.CharField(max_length=10, choices=VERTICE_CHOICES, verbose_name="Vértice")
    v1 = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="V1", blank=True, null=True)
    v3 = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="V3", blank=True, null=True)
    v4 = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="V4", blank=True, null=True)
    ejecutada = models.CharField(max_length=20, choices=ESTADO_CHOICES, verbose_name="Estado de Ejecución")
    centros_salud = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Centros de Salud (V3)", blank=True, null=True)
    educacion = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Educación", blank=True, null=True)
    deporte_recreacion = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Deporte, Recreación, Esparcimiento y Otros", blank=True, null=True)
    unidades_militares = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Unidades Militares", blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Registro BSD"
        verbose_name_plural = "Registros BSD"
        ordering = ['item']
    
    def __str__(self):
        return f"{self.item} - {self.institucion[:50]}"
