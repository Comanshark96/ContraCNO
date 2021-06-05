from django.utils.timezone import now
from django.db import models
from EntregaDNI.models import Unidad, Integrante, Domiciliarias


class Sede(models.Model):
    """ Representa una sede de enrolamiento """

    id = models.BigAutoField(primary_key=True)
    colonia = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    fecha = models.DateField(default=now)
    unidades = models.ManyToManyField(Unidad, related_name='sedes', blank=True)
    entregadas = models.ManyToManyField(Integrante, related_name='sedes', blank=True)

    def __str__(self):
        return f'{self.colonia} - {self.nombre}'

    def total_entregadas(self):
        """ Devuelve el total de DNIs entregadas por sede """

        suma = 0
        suma_dom = 0
        
        dom = Domiciliarias.objects.filter(fecha=self.fecha)

        if dom:
            for d in dom:
                suma_dom += d.informe()['total']

        for integrante in self.entregadas.all():
            suma += integrante.sobres.filter(fecha=self.fecha).count()

        return suma - suma_dom

        return
    def total(self):
        suma = 0

        for enrol in self.recibos.all():
            suma += enrol.cantidad

        return suma

    class Meta:
        ordering = ('-fecha',)


class Enrolamiento(models.Model):
    """ Representa un dato de enrolamiento """

    id = models.BigAutoField(primary_key=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='recibos', editable=False)
    recibo_inicio = models.CharField(max_length=30, unique=True)
    recibo_final = models.CharField(max_length=30, unique=True)
    cantidad = models.IntegerField()

    # Enroladores
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='enrolamientos')

    def __str__(self):
        return f'Unidad {self.unidad.numero} en {self.sede.nombre}'
