from datetime import date
from django import forms


class FormEntregadas(forms.Form):

    fecha_entregadas = forms.DateField(required=True, widget=forms.DateInput(attrs={'class': 'form-control datetimepicker',
                                                                         'placeholder': 'Fecha de consulta',
                                                                         'data-target': '#fecha-entregadas'}))


class FormActaCierre(forms.Form):

    fecha = forms.DateField(required=True, widget=forms.DateInput(attrs={'class':'form-control datetimepicker',
                                                          'placeholder': 'Fecha de consulta',
                                                          'data-target': '#fecha'}))
