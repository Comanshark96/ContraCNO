import datetime
from django.http import Http404, HttpResponseForbidden
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, FormView
from . import models, forms


class EscanerCaja(CreateView):

    model = models.Caja
    form_class = forms.FormCaja
    template_name = 'EntregaDNI/escaner-caja.html'
    success_url = reverse_lazy('EscanerCaja')

    def get_context_data(self, **kwargs):
        """ Añade solo los centros del equipo """

        usuario = self.request.user.integrante
        contexto = super().get_context_data(**kwargs)
        if usuario.es_supervisor:
            contexto['form'].fields['centro'].queryset = models.Centro.objects.filter(unidad__equipo=usuario.equipo_supervisado)
        else:
            contexto['form'].fields['centro'].queryset = models.Centro.objects.filter(unidad__equipo=usuario.unidad.equipo)

        return contexto

class ListaCajas(ListView):
    """ Lista las cajas en una tabla """

    model = models.Caja
    template_name = 'EntregaDNI/lista-cajas.html'

    def get_queryset(self):
        usuario = self.request.user.integrante
        if usuario.es_supervisor:
            return self.model.objects.filter(centro__unidad__equipo=usuario.equipo_supervisado)
        else:
            return self.model.objects.filter(centro__unidad__equipo=usuario.unidad.equipo)


class ListaCentros(ListView):
    """ Lista los centros de entrega en una tabla """

    model = models.Centro
    template_name = 'EntregaDNI/lista-centros.html'

    def get_queryset(self):
        usuario = self.request.user.integrante
        if usuario.es_supervisor:
            return self.model.objects.filter(unidad__equipo=usuario.equipo_supervisado)
        else:
            return self.model.objects.filter(unidad__equipo=usuario.unidad.equipo)


class EditarCentro(UpdateView):
    """ Edita un centro de entrega """

    model = models.Centro
    object_id = 'pk'
    form_class = forms.FormCentro
    template_name = 'EntregaDNI/form-centro.html'
    success_url = reverse_lazy('ListaCentros')

    def dispatch(self, request, *args, **kwargs):
        usuario = request.user.integrante
        del_equipo = bool()

        if usuario.es_supervisor:
            del_equipo = usuario.equipo_supervisado == self.get_object().equipo
        else:
            del_equipo = usuario.unidad.equipo == self.get_object().equipo
            
        if del_equipo:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404

class CrearCentro(CreateView):
    """ Crea un centro de entrega """

    model = models.Centro
    object_id = 'pk'
    form_class = forms.FormCentro
    template_name = 'EntregaDNI/form-centro.html'
    success_url = reverse_lazy('ListaCentros')

    def form_valid(self, form):
        usuario = self.request.user.integrante
        centro = form.save(commit=False)

        if not usuario.es_supervisor:
            centro.centro = usuario.unidad
            centro.save()

        return redirect(reverse_lazy('ListaCentros'))


class EscanerSobre(CreateView):
    """ Crea un registro de un sobre """

    model = models.Sobre
    form_class = forms.FormSobre
    template_name = 'EntregaDNI/escaner-sobre.html'
    success_url = reverse_lazy('EscanerSobre')

class ListaSobres(ListView):
    """ Lista los sobres escaneados """

    model = models.Sobre
    template_name = 'EntregaDNI/lista-sobres.html'

    def get_queryset(self):
        """ Lista solo los sobres que escaneó el equipo """
        usuario = self.request.user.integrante

        if usuario.es_supervisor:
            return self.model.objects.filter(caja__centro__unidad__equipo=usuario.equipo_supervisado)
        else:
            return self.model.objects.filter(caja__centro__unidad__equipo=usuario.unidad.equipo)


class Informes(TemplateView):

    template_name = 'EntregaDNI/informes.html'

class ActaCierre(TemplateView):

    template_name = 'EntregaDNI/acta-cierre.html'

    def get_context_data(self, **kwargs):
        usuario = self.request.user.integrante
        contexto = super().get_context_data(**kwargs)
        fecha = datetime.datetime.strptime(self.request.GET['fecha'], '%d/%m/%Y')
        cajas = None
        resultados = [] 

        if usuario.es_supervisor:
            cajas = models.Caja.objects.filter(centro__unidad__equipo=usuario.equipo_supervisado)
        else:
            cajas = models.Caja.objects.filter(centro__unidad__equipo=usuario.unidad.equipo)

        for caja in cajas:
            apertura = caja.cantidad - caja.sobre.filter(fecha__lt=fecha).count()
            entregadas = caja.sobre.filter(fecha=fecha).count()
            resultados.append({'caja': caja.codigo, 'apertura': apertura, 'entregadas': entregadas, 'cierre': apertura - entregadas})

        contexto['resultados'] = resultados
        contexto['fecha'] = fecha

        return contexto
