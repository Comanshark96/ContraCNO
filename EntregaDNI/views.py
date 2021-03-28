import datetime
from django.http import Http404, HttpResponseForbidden
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, ListView, UpdateView
from django.views.decorators.cache import never_cache 
from django.utils.decorators import method_decorator
from .numero_letras import numero_a_letras
from . import models, forms


def inicio(request, *args, **kwargs):
    return redirect(reverse_lazy('ListaCentros'))
    
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
            centro.unidad = usuario.unidad
            centro.save()

        return redirect(reverse_lazy('ListaCentros'))


class EscanerSobre(CreateView):
    """ Crea un registro de un sobre """

    model = models.Sobre
    form_class = forms.FormSobre
    template_name = 'EntregaDNI/escaner-sobre.html'

    def get_success_url(self):
        return reverse_lazy('EscanerSobre') + '?exito'

    def form_valid(self, form):
        sobre = form.save(commit=False)
        existe_sobre = bool(models.Sobre.objects.filter(codigo=sobre.codigo, caja=sobre.caja))

        if existe_sobre:
            return redirect(reverse_lazy('EscanerSobre'))
        else:
            sobre.save()
            return redirect(self.get_success_url())


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

    def get_context_data(self, **kwargs):
        usuario = self.request.user.integrante
        contexto = super().get_context_data(**kwargs)

        formulario = forms.FormActaCierre()

        if usuario.es_supervisor:
            formulario.fields['unidad'].queryset = models.Unidad.objects.filter(equipo=usuario.equipo_supervisado)
        else:
            formulario.fields['unidad'].queryset = models.Unidad.objects.filter(equipo=usuario.unidad.equipo)

        contexto['form'] = formulario
        
        return contexto

@method_decorator(never_cache, 'dispatch')
class ActaCierre(TemplateView):

    template_name = 'EntregaDNI/acta-cierre.html'

    def get_context_data(self, **kwargs):
        usuario = self.request.user.integrante
        contexto = super().get_context_data(**kwargs)
        formulario = forms.FormActaCierre(self.request.GET)
        total = 0

        if formulario.is_valid():
            unidad = formulario.cleaned_data['unidad']
            fecha = formulario.cleaned_data['fecha']
            cajas = None
            resultados = [] 
            total_entregadas = 0
            total_cierre = 0

            if usuario.es_supervisor:
                cajas = models.Caja.objects.filter(centro__unidad__equipo=usuario.equipo_supervisado, centro__unidad=unidad)
            else:
                cajas = models.Caja.objects.filter(centro__unidad__equipo=usuario.unidad.equipo, centro__unidad=unidad)

            for caja in cajas:
                apertura = caja.cantidad - caja.sobre.filter(fecha__lt=fecha).count()
                entregadas = caja.sobre.filter(fecha=fecha).count()
                cierre = apertura - entregadas
                total_entregadas += entregadas
                total_cierre += cierre
                resultados.append({'caja': caja.codigo, 'apertura': apertura, 'entregadas': entregadas, 'cierre': cierre})

            contexto['resultados'] = resultados
            contexto['fecha'] = fecha
            contexto['total_entregadas'] = total_entregadas
            contexto['total_cierre'] = total_cierre
            contexto['unidad'] = unidad

        return contexto

class ActaCierreImprimir(ActaCierre):

    template_name = 'EntregaDNI/acta-cierre-print.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        contexto['resultados_letras'] = len(contexto['resultados'])
        contexto['total_entregadas_letras'] = numero_a_letras(contexto['total_entregadas'])
        contexto['total_cierre_letras'] = numero_a_letras(contexto['total_cierre'])
