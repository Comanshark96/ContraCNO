from django import forms
from . import models as m


class FormularioSede(forms.ModelForm):
    """ Formulario para crear/editar sedes """

    class Meta:
        model = m.Sede
        fields = '__all__'
        widgets = {
            'colonia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Colonia'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de sede'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de sede'}),
            'unidades': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

class FormularioRecibo(forms.ModelForm):
    """ Formulario para registrar recibo """

    class Meta:
        model = m.Recibo
        fields = ('codigo',)
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'})
        }
