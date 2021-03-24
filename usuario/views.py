from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from . import forms


class Ingreso(LoginView):

    template_name = 'usuario/ingreso.html'
    form_class = forms.FormAuth
    success_url = reverse_lazy('ListaCentros')
