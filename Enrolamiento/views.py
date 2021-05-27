from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from . import models as m, forms as f


class ListaSedes(ListView):
    """ Lista las sedes de enrolamiento """

    model = m.Sede
    template_name = 'Enrolamiento/lista-sedes.html'

    def get_queryset(self):
        usuario = self.user.integrante
        query = None

        if usuario.es_supervisado:
            query = m.Sede.objects.filter(unidades.equipo=usuario.equipo_supervisado)
        else:
            query = m.Sede.objects.filter(unidades.equipo=usuario.equipo)

        return query

class EscanerRecibo(CreateView):
    """ Escanea los recibos de enrolamiento """

    model = m.Recibo
    template_name = 'Enrolamiento/escaner-recibo.html'
    form_class = f.FormularioRecibo
    success_url = reverse_lazy('EscanerRecibo')

    def form_valid(self, form):
        recibo = form.save(commit=False)
        recibo
