from django import forms
from django.shortcuts import get_object_or_404
from . import models


class FormCaja(forms.ModelForm):

    class Meta:
        model = models.Caja
        fields = '__all__'
        widgets = {
                'codigo': forms.TextInput(attrs={
                    'class': 'form-control',
                    'readonly': True,
                    'placeholder': 'Código de caja'
                    }),
                'centro': forms.Select(attrs={'class': 'form-control'}),
                'cantidad': forms.NumberInput(attrs={'class': 'form-control'})
                }


class FormCentro(forms.ModelForm):

    class Meta:
        model = models.Centro
        fields = ('nombre',)
        widgets = {'nombre': forms.TextInput(attrs={'class': 'form-control',
            'placeholder': 'Nombre del centro'})}


class FormSobre(forms.ModelForm):

    caja = forms.CharField(required=True, max_length=7, widget=forms.TextInput(attrs={'class': 'form-control',
        'placeholder': 'Código QR de la caja', 'readonly': True}))

    class Meta:
        model = models.Sobre
        fields = ('codigo',)
        widgets = {
                'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código QR del sobre', 'readonly': True}),
        }

    def save(self, commit=True):
        """ Reescribe el método de guardar """

        cod_sobre = self.cleaned_data['codigo']
        cod_caja = self.cleaned_data['caja']

        caja = models.Caja.objects.get(codigo=cod_caja)
        nuevo_sobre = models.Sobre(codigo=cod_sobre)
        nuevo_sobre.caja = caja

        if commit:
            nuevo_sobre.save()

        return nuevo_sobre

    def clean_caja(self):
        """ Valida si la caja existe """

        caja = None
        cod_caja = codigo=self.cleaned_data['caja']
        caja = models.Caja.objects.filter(codigo=cod_caja)

        if not caja:
            raise forms.ValidationError('No se encuentra la caja en el sistema')
        
        return cod_caja

class FormEntregadas(forms.Form):

    fecha_entregadas = forms.DateField(required=True, widget=forms.DateInput(attrs={'class': 'form-control datetimepicker',
                                                                         'placeholder': 'Fecha de consulta',
                                                                         'data-target': '#fecha-entregadas'}))


class FormActaCierre(forms.ModelForm):

    fecha = forms.DateField(required=True, widget=forms.DateInput(attrs={'class':'form-control datetimepicker',
                                                          'placeholder': 'Fecha de consulta',
                                                          'data-target': '#fecha'}))

    class Meta:
        model = models.Centro
        fields = ('unidad',)
        widgets = {
                'unidad': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Escoja una unidad'})
            }

