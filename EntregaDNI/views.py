from django.utils.timezone import datetime
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DeleteView
from django.views.decorators.cache import never_cache 
from django.utils.decorators import method_decorator
from django.contrib import messages
from .numero_letras import numero_a_letras
from . import models, forms


def inicio(request, *args, **kwargs):
    return redirect(reverse_lazy('ListaCentros'))


@never_cache
def sobres_hoy(request, *args, **kwargs):
    sobres = request.user.integrante.sobres.filter(fecha=datetime.today()).count()
    enrolados = request.user.integrante.enrolamientos.filter(fecha=datetime.today()).count()
    escaneados = request.user.integrante.escaneados.filter(fecha=datetime.today()).count()
    return HttpResponse(str([sobres, enrolados, escaneados]))
    
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
            del_equipo = usuario.equipo_supervisado == self.get_object().unidad.equipo
        else:
            del_equipo = usuario.unidad.equipo == self.get_object().unidad.equipo
            
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

        if usuario.es_supervisor:
            return self.model.objects.filter(caja__centro__unidad__equipo=usuario.equipo_supervisado)
        else:
            return self.model.objects.filter(usuario=usuario)


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


class Informes(TemplateView):

    template_name = 'EntregaDNI/informes.html'

    def get_context_data(self, **kwargs):
        usuario = self.request.user.integrante
        contexto = super().get_context_data(**kwargs)

        formulario = forms.FormActaCierre()
        form_entregadas = forms.FormEntregadas()

        if usuario.es_supervisor:
            formulario.fields['unidad'].queryset = models.Unidad.objects.filter(equipo=usuario.equipo_supervisado)
        else:
            formulario.fields['unidad'].queryset = models.Unidad.objects.filter(equipo=usuario.unidad.equipo)


        contexto['form'] = formulario
        contexto['entregadas'] = form_entregadas
        
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
            total_apertura = 0
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
                total_apertura += apertura
                total_entregadas += entregadas
                total_cierre += cierre
                resultados.append({'caja': caja.codigo, 'apertura': apertura, 'entregadas': entregadas, 'cierre': cierre,
                    'apertura_letras': numero_a_letras(apertura), 'cierre_letras': numero_a_letras(cierre)})

            contexto['resultados'] = resultados
            contexto['resultados_letras'] = numero_a_letras(len(resultados))
            contexto['total_apertura'] = total_apertura
            contexto['total_apertura_letras'] = numero_a_letras(total_apertura)
            contexto['fecha'] = fecha
            contexto['total_entregadas'] = total_entregadas
            contexto['total_cierre'] = total_cierre
            contexto['total_cierre_letras'] = numero_a_letras(total_cierre)
            contexto['unidad'] = unidad

        return contexto

class ActaCierreImprimir(ActaCierre):

    template_name = 'EntregaDNI/acta-cierre-print.html'


class ActaAperturaImprimir(ActaCierre):

    template_name = 'EntregaDNI/acta-apertura-print.html'


@method_decorator(never_cache, 'dispatch')
class EntregadosUsuario(ListView):
    """ Detalla la cantidad de sobres entregados por enrolador """

    model = models.User
    template_name = 'EntregaDNI/entregadas-usuario.html'

    def get_queryset(self):
        usuario = self.request.user.integrante
        equipo = None

        if usuario.es_supervisor:
            equipo = usuario.equipo_supervisado
        else:
            equipo = usuario.unidad.equipo

        return self.model.objects.filter(integrante__unidad__equipo=equipo).exclude(integrante__es_supervisor=True)

    def get_context_data(self, **kwargs):
        usuario = self.request.user.integrante
        ctx = super().get_context_data(**kwargs)
        formulario = forms.FormEntregadas(self.request.GET)

        if formulario.is_valid():
            fecha = formulario.cleaned_data['fecha_entregadas']
            print(fecha)
            usuarios = []
            hoy_total = 0
            total = 0

            for user in ctx['object_list']:
                nuevo_resultado = {'nombre': user.get_full_name(),
                                   'hoy': models.Sobre.objects.por_fecha(fecha, user.integrante),
                                   'escaneado': user.integrante.escaneados.filter(fecha=datetime.today()).count(),
                                   'total': user.integrante.sobres.count()}

                usuarios.append(nuevo_resultado)
                total += nuevo_resultado['total']
                hoy_total += nuevo_resultado['hoy']

            ctx['usuarios'] = usuarios
            ctx['htotal'] = hoy_total
            ctx['total'] = total

            return ctx
