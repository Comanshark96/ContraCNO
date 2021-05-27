""" MODELOS DE PARA ENTREGA DE DNI

Estos modelos representan el inventario que se necesita para la
entrega de DNIs por parte del proyecto Identifícate.

Autor: Carlos E. Rivera
Licencia: GPLv3
"""

from django.db import models
from django.contrib.auth.models import User


class Integrante(models.Model):

    id = models.BigAutoField(primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='integrante')
    es_supervisor = models.BooleanField(default=False)
    unidad = models.ForeignKey('Unidad', on_delete=models.CASCADE, related_name='integrantes', blank=True, null=True)

    def __str__(self):
        return self.usuario.username + ' - ' + self.usuario.get_full_name()


class Equipo(models.Model):
    """ Representa un equipo de enrolamiento """

    id = models.BigAutoField(primary_key=True)
    supervisor = models.OneToOneField(Integrante, on_delete=models.CASCADE, related_name='equipo_supervisado')
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Unidad(models.Model):
    """ Representa una unidad de enrolamiento """

    id = models.BigAutoField(primary_key=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='unidades')
    numero = models.CharField(max_length=30)

    def __str__(self):
        return f'Unidad {self.numero} de {self.equipo.nombre}'


class Centro(models.Model):
    """ Representa un Centro de entrega """

    id = models.BigAutoField(primary_key=True)
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='centro')
    nombre = models.CharField(max_length=100)


    def __str__(self):
        return self.nombre


class Caja(models.Model):
    """ Representa una caja de sobres """

    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(max_length=7, unique=True)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE, related_name='caja')
    cantidad = models.PositiveSmallIntegerField(default=240)

    def __str__(self):
        return f'{self.codigo} - {self.centro.nombre}'

class ManejadorSobre(models.Manager):

    def por_fecha(self, fecha, usuario):
        return self.filter(fecha=fecha, usuario=usuario).count()


class Sobre(models.Model):
    """ Representa un sobre que contiene la DNI """

    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(max_length=9)
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='sobre')
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Integrante, on_delete=models.CASCADE, related_name='sobres')
    escaner = models.ForeignKey(Integrante, on_delete=models.SET_NULL, related_name='escaneados', null=True)

    objects = ManejadorSobre()

    def __str__(self):
        return f'sobre {self.codigo} de caja {self.caja.codigo}'

    class Meta:
        ordering = ('-fecha',)


