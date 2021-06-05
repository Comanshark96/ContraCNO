from django.utils.timezone import datetime
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DeleteView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages
from . import models, forms


def inicio(request, *args, **kwargs):
    return redirect(reverse_lazy('ListaCentros'))


@never_cache
def sobres_hoy(request, *args, **kwargs):
    sobres = request.user.integrante.sobres.filter(fecha=datetime.today()).count()
    escaneados = request.user.integrante.escaneados.filter(fecha=datetime.today()).count()
    return HttpResponse(str([sobres, escaneados]))

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
            contexto['form'].fields['centro'].queryset = models.Centro.objects.filter(equipo=usuario.equipo_supervisado)
        else:
            contexto['form'].fields['centro'].queryset = models.Centro.objects.filter(equipo=usuario.unidad.equipo)

        return contexto

class ListaCajas(ListView):
    """ Lista las cajas en una tabla """

    model = models.Caja
    template_name = 'EntregaDNI/lista-cajas.html'
    paginate_by = 20

    def get_queryset(self):
        usuario = self.request.user.integrante
        query = None

        if usuario.es_supervisor:
            query = self.model.objects.filter(centro__equipo=usuario.equipo_supervisado)
        else:
            query = self.model.objects.filter(centro__equipo=usuario.unidad.equipo)

        if 'buscar' in self.request.GET and self.request.GET['buscar'] is not None:
            buscar = self.request.GET['buscar']
            query = query.filter(Q(codigo__icontains=buscar) | Q(centro__nombre__icontains=buscar))

        return query

class ListaCentros(ListView):
    """ Lista los centros de entrega en una tabla """

    model = models.Centro
    template_name = 'EntregaDNI/lista-centros.html'

    def get_queryset(self):
        usuario = self.request.user.integrante
        query = None

        if usuario.es_supervisor:
            query = self.model.objects.filter(equipo=usuario.equipo_supervisado)
        else:
            query = self.model.objects.filter(equipo=usuario.unidad.equipo)

        if 'buscar' in self.request.GET and self.request.GET['buscar'] is not None:
            buscar = self.request.GET['buscar']
            query = query.filter(nombre__icontains=buscar)

        return query


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

        if usuario.es_supervisor:
            centro.equipo = usuario.equipo_supervisado
        else:
            centro.equipo = usuario.equipo

        centro.save()

        return redirect(reverse_lazy('ListaCentros'))


class EscanerSobre(CreateView):
    """ Crea un registro de un sobre """

    model = models.Sobre
    form_class = forms.FormSobre
    template_name = 'EntregaDNI/escaner-sobre.html'
    success_url = reverse_lazy('EscanerSobre')

    def form_valid(self, form):
        sobre = form.save(commit=False)
        existe_sobre = models.Sobre.objects.filter(codigo=sobre.codigo, caja=sobre.caja)

        if existe_sobre:
            messages.warning(self.request, f'El {existe_sobre[0]} ya fue registrado por {existe_sobre[0].usuario}')
        else:
            sobre.usuario = self.request.user.integrante
            sobre.save()
            messages.success(self.request, f'El {sobre} se registró correctamente')

        return redirect(self.success_url)


class EscanerSobreUsuario(EscanerSobre):
    """ Extienede el EscanerSobre seleccionando el usuario que entrega """

    form_class = forms.FormSobreUsuario
    template_name = 'EntregaDNI/escaner-sobre-usuario.html'
    success_url = reverse_lazy('EscanerSobreUsuario')

    def form_valid(self, form):
        sobre = form.save(commit=False)
        usuario = self.request.user.integrante
        existe_sobre = models.Sobre.objects.filter(codigo=sobre.codigo, caja=sobre.caja)
        form = self.form_class()

        if usuario.es_supervisor:
            form.fields['usuario'].queryset = models.Integrante.objects.filter(equipo_supervisado=usuario.equipo_supervisado).exclude(es_supervisor=True)

        else:
            form.fields['usuario'].queryset = models.Integrante.objects.filter(unidad__equipo=usuario.unidad.equipo).exclude(es_supervisor=True)


        if existe_sobre:
            messages.warning(self.request, f'El {existe_sobre[0]} ya fue registrado por {existe_sobre[0].usuario}')
        else:
            if sobre.usuario != usuario:
                sobre.escaner = usuario

            sobre.save()
            messages.success(self.request, f'El {sobre} se registró correctamente para {sobre.usuario.usuario.get_full_name()}')

        return redirect(self.success_url)


class ListaSobres(ListView):
    """ Lista los sobres escaneados """

    model = models.Sobre
    template_name = 'EntregaDNI/lista-sobres.html'
    paginate_by = 50

    def get_queryset(self):
        """ Lista solo los sobres que escaneó el equipo """
        usuario = self.request.user.integrante
        query = None

        if usuario.es_supervisor:
            query = self.model.objects.filter(caja__centro__equipo=usuario.equipo_supervisado)
        else:
            query = self.model.objects.filter(usuario=usuario)

        if 'buscar' in self.request.GET and self.request.GET['buscar'] is not None:
            buscar = self.request.GET['buscar']
            query = query.filter(Q(codigo__icontains=buscar) | Q(caja__codigo__icontains=buscar))

        return query


class EliminarSobre(DeleteView):
    """ Elimina un sobre en el sistema """

    template_name = 'EntregaDNI/eliminar-sobre.html'
    model = models.Sobre
    success_url = reverse_lazy('ListaSobres')

    def dispatch(self, request, *args, **kwargs):
        """ Incluye la eliminación de solo los sobres dueños """

        if self.get_object().usuario == request.user.integrante:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        messages.success(self.request, f'Se ha eliminado el sobre correctamente')
        return super().post(request, *args, **kwargs)
