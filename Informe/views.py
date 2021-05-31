from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache 
from EntregaDNI.models import Caja, Sobre, User
from .numero_letras import numero_a_letras
from . import forms


class Informes(TemplateView):

    template_name = 'EntregaDNI/informes.html'

    def get_context_data(self, **kwargs):
        usuario = self.request.user.integrante
        contexto = super().get_context_data(**kwargs)

        formulario = forms.FormActaCierre()
        form_entregadas = forms.FormEntregadas()

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
            fecha = formulario.cleaned_data['fecha']
            cajas = None
            resultados = [] 
            total_apertura = 0
            total_entregadas = 0
            total_cierre = 0

            if usuario.es_supervisor:
                cajas = Caja.objects.filter(centro__equipo=usuario.equipo_supervisado)
            else:
                cajas = Caja.objects.filter(centro__equipo=usuario.unidad.equipo)

            for caja in cajas:
                apertura = caja.cantidad - caja.sobres.filter(fecha__lt=fecha).count()
                entregadas = caja.sobres.filter(fecha=fecha).count()
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
            contexto['unidad'] = 1

        return contexto

class ActaCierreImprimir(ActaCierre):

    template_name = 'EntregaDNI/acta-cierre-print.html'


class ActaAperturaImprimir(ActaCierre):

    template_name = 'EntregaDNI/acta-apertura-print.html'


@method_decorator(never_cache, 'dispatch')
class EntregadosUsuario(ListView):
    """ Detalla la cantidad de sobres entregados por enrolador """

    model = User
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

        if 'fecha_entregadas' in self.request.GET and self.request.GET['fecha_entregadas'] is not None:
            formulario = forms.FormEntregadas(self.request.GET)
        else:
            formulario = forms.FormEntregadas({'fecha_entregadas': datetime.today()})

        if formulario.is_valid():
            fecha = formulario.cleaned_data['fecha_entregadas']
            print(fecha)
            usuarios = []
            hoy_total = 0
            escaneado = 0
            enrolado = 0
            total = 0

            for user in ctx['object_list']:
                nuevo_resultado = {'nombre': user.get_full_name(),
                                   'hoy': Sobre.objects.por_fecha(fecha, user.integrante),
                                   'escaneado': user.integrante.escaneados.filter(fecha=fecha).count(),
                                   'enrolado': user.integrante.enrolados.filter(sede__fecha=fecha).count(),
                                   'total': user.integrante.sobres.count()}

                usuarios.append(nuevo_resultado)
                total += nuevo_resultado['total']
                escaneado += nuevo_resultado['escaneado']
                enrolado += nuevo_resultado['enrolado']
                hoy_total += nuevo_resultado['hoy']

            ctx['entregadas'] = formulario
            ctx['usuarios'] = usuarios
            ctx['htotal'] = hoy_total
            ctx['escaneado'] = escaneado
            ctx['enrolado'] = enrolado
            ctx['total'] = total

            return ctx
