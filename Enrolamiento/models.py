from django.utils.timezone import now
from django.db import models
from EntregaDNI.models import Unidad, Integrante


class Sede(models.Model):
    """ Representa una sede de enrolamiento """

    id = models.BigAutoField(primary_key=True)
    colonia = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    fecha = models.DateField(default=now)
    unidades = models.ManyToManyField(Unidad, related_name='sedes')

    def __str__(self):
        return f'{self.colonia} - {self.nombre}'

    class Meta:
        ordering = ('-fecha',)


class Enrolamiento(models.Model):
    """ Representa un dato de enrolamiento """

    id = models.BigAutoField(primary_key=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='recibos', editable=False)
    recibo_inicio = models.CharField(max_length=30, unique=True)
    recibo_final = models.CharField(max_length=30, unique=True)

    # Enroladores
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='enrolamientos')

    def __str__(self):
        return f'Unidad {self.unidad.numero} en {self.sede.nombre}'

    class Meta:
        ordering = ('hora',)
