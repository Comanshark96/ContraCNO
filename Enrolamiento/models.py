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

    def enrolamientos(self):
        suma = 0
        for unidad in self.enrolamientos_por_unidad():
            suma += unidad[1]

        return suma

    def enrolamientos_por_unidad(self):
        unidades = list()

        for unidad in self.unidades.all():
            unidades.append((unidad, unidad.enrolados.filter(fecha=self.fecha).count(),))

        return unidades

    class Meta:
        ordering = ('-fecha',)


class Recibo(models.Model):
    """ Representa un recibo de enrolamiento """

    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(max_length=30, unique=True)
    hora = models.TimeField(auto_now_add=True)
    fecha = models.DateField(auto_now_add=True)

    # Enroladores
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='enrolados')
    usuario = models.ForeignKey(Integrante, on_delete=models.CASCADE, related_name='enrolamientos')
