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

    def informe(self):
        """ Crea un informe de la sede """

        informe = {'unidades': [], 'enrolados': 0} 

        for unidad in self.unidades.all():
            recibos = unidad.recibos.filter(sede=self)
            total = recibos.count()

            informe['unidades'].append({
                'unidad': unidad,
                'primer_recibo': recibos.first(),
                'ultimo_recibo': recibos.last(),
                'total': total})
            informe['enrolados'] += total

        return informe

    def __str__(self):
        return f'{self.colonia} - {self.nombre}'

    class Meta:
        ordering = ('-fecha',)


class Recibo(models.Model):
    """ Representa un recibo de enrolamiento """

    id = models.BigAutoField(primary_key=True)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='recibos', editable=False)
    codigo = models.CharField(max_length=30, unique=True)
    hora = models.TimeField(auto_now_add=True)

    # Enroladores
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='recibos')
    usuario = models.ForeignKey(Integrante, on_delete=models.CASCADE, related_name='enrolados')

    def __str__(self):
        return f'{self.sede.nombre}: {self.codigo}'

    class Meta:
        ordering = ('hora',)
