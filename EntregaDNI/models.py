""" MODELOS DE PARA ENTREGA DE DNI

Estos modelos representan el inventario que se necesita para la
entrega de DNIs por parte del proyecto Identifícate.

Autor: Carlos E. Rivera
Licencia: GPLv3
"""

from django.contrib.auth.models import User
from django.db import models


class Integrante(models.Model):

    id = models.BigAutoField(primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='integrante')
    es_supervisor = models.BooleanField(default=False)
    unidad = models.ForeignKey('Unidad', on_delete=models.CASCADE, related_name='integrantes', blank=True, null=True)

    def __str__(self):
        return self.usuario.get_full_name()


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
    kit = models.CharField(max_length=4)

    def __str__(self):
        return f'Unidad {self.numero} de {self.equipo.nombre}'


class Centro(models.Model):
    """ Representa un Centro de entrega """

    id = models.BigAutoField(primary_key=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='centros')
    nombre = models.CharField(max_length=100)


    def __str__(self):
        return self.nombre


class Caja(models.Model):
    """ Representa una caja de sobres """

    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(max_length=7)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE, related_name='cajas')
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
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='sobres')
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    usuario = models.ForeignKey(Integrante, on_delete=models.CASCADE, related_name='sobres')
    escaner = models.ForeignKey(Integrante, on_delete=models.SET_NULL, related_name='escaneados', null=True)

    objects = ManejadorSobre()

    def __str__(self):
        return f'sobre {self.codigo} de caja {self.caja.codigo}'

    class Meta:
        ordering = ('-fecha', '-hora',)


class Domiciliarias(models.Model):
    """ Representa una entrega de DNI domiciliarias """

    integrantes = models.ManyToManyField(Integrante, related_name='domiciliarias')
    fecha = models.DateField(auto_now_add=True)
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()

    def informe(self):
        informe = {'usuarios': [], 'total': 0}

        for usuario in self.integrantes.all():
            usuario_dict = {'nombre': usuario.usuario.get_full_name(),
                            'sobres': usuario.sobres.filter(fecha=self.fecha,
                                                            hora__gte=self.hora_inicio,
                                                            hora__lte=self.hora_final)}

            informe['total'] += usuario_dict['sobres'].count()
            informe['usuarios'].append(usuario_dict)

        return informe
