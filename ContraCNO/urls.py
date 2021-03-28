"""ContraCNO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from usuario.views import Ingreso, LogoutView
from EntregaDNI import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_required(views.inicio), name='Inicio'),
    path('ingreso', Ingreso.as_view(), name='Ingreso'),
    path('cierre', login_required(LogoutView.as_view()), name='Cierre'),
    path('escaner-caja', login_required(views.EscanerCaja.as_view()), name='EscanerCaja'),
    path('cajas', login_required(views.ListaCajas.as_view()), name='ListaCajas'),
    path('centros', login_required(views.ListaCentros.as_view()), name='ListaCentros'),
    path('editar-centro/<int:pk>', login_required(views.EditarCentro.as_view()), name='EditarCentro'),
    path('crear-centro', login_required(views.CrearCentro.as_view()), name='CrearCentro'),
    path('escaner-sobre', login_required(views.EscanerSobre.as_view()), name='EscanerSobre'),
    path('sobres', login_required(views.ListaSobres.as_view()), name='ListaSobres'),
    path('acta-cierre', login_required(views.ActaCierre.as_view()), name='ActaCierre'),
    path('acta-cierre/imprimir', login_required(views.ActaCierreImprimir.as_view()), name='ActaCierreImprimir'),
    path('acta-apertura/imprimir', login_required(views.ActaAperturaImprimir.as_view()), name='ActaAperturaImprimir'),
    path('informes', login_required(views.Informes.as_view()), name='Informes'),
]
