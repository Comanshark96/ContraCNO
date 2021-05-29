from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from . import models as m, forms as f


class CrearSede(CreateView):
    """ Crea una sede de enrolamiento """

    model = m.Sede
    form_class = f.FormularioSede
    template_name = 'Enrolamiento/crear-sede.html'
    success_url = reverse_lazy('ListaSedes')

    def form_valid(self, form):
        messages.success(self.request, 'Se ha creado una sede correctamente')
        return super().form_valid(form)


class EditarSede(UpdateView):

    model = m.Sede
    form_class = f.FormularioSede
    template_name = 'Enrolamiento/crear-sede.html'
    success_url = reverse_lazy('ListaSedes')

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        return form_class(True, **self.get_form_kwargs())

    def form_valid(self, form):
        messages.success(self.request, 'Se ha editado correctamente')
        return super().form_valid(form)


class EliminarSede(DeleteView):
    """ Elimina una sede de enrolamientos """

    model = m.Sede
    template_name = 'Enrolamiento/eliminar-sede.html'
    success_url = reverse_lazy('ListaSedes')

    def post(self, request, *args, **kwargs):
        messages.success(request, f'Se ha eliminado la sede {{ object.nombre }}')
        return super().post(request, *args, **kwargs)

class DetalleSede(DetailView):
    """ Detalla una sede de enrolamiento """

    model = m.Sede
    template_name= 'Enrolamiento/detalle-sede.html'

class ListaSedes(ListView):
    """ Lista las sedes de enrolamiento """

    model = m.Sede
    template_name = 'Enrolamiento/lista-sedes.html'
    paginate_by = 20

    def get_queryset(self):
        usuario = self.request.user.integrante
        query = None

        if usuario.es_supervisor:
            query = m.Sede.objects.filter(unidades__equipo=usuario.equipo_supervisado)
        else:
            query = m.Sede.objects.filter(unidades__equipo=usuario.unidad.equipo)

        return query

class EscanerRecibo(CreateView):
    """ Escanea los recibos de enrolamiento """

    model = m.Recibo
    template_name = 'Enrolamiento/escaner-recibo.html'
    form_class = f.FormularioRecibo
    success_url = reverse_lazy('EscanerRecibo')

    def form_valid(self, form):
        recibo = form.save(commit=False)
        recibo.usuario = self.request.user.integrante
        recibo.save()
        messages.success(self.request, 'Se ha registrado el recibo correctamente')

        return redirect(self.success_url)
