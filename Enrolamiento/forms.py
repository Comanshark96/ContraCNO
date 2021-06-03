import datetime
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from . import models as m


class FormularioSede(forms.ModelForm):
    """ Formulario para crear/editar sedes """

    def __init__(self, edicion=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not edicion:
            self.fields['unidades'].queryset = m.Unidad.objects.exclude(sedes__fecha=datetime.date.today())

    class Meta:
        model = m.Sede
        fields = ('colonia', 'nombre', 'unidades',)
        widgets = {
            'colonia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Colonia'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de sede'}),
            'unidades': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

class FormularioRecibo(forms.ModelForm):
    """ Formulario para registrar recibo """

    class Meta:
        model = m.Enrolamiento
        fields = ('recibo_inicio', 'recibo_final',)
        widgets = {
            'reicibo_inicio': forms.TextInput(attrs={'class': 'form-control'})
            'reicibo_final': forms.TextInput(attrs={'class': 'form-control'})
        }

    def validar_recibo(self, codigo):
        """ Valida el codigo del recibo """
        
        try:
            unidad = m.Unidad.objects.get(kit=codigo[:4])
        except ObjectDoesNotExist:
            raise forms.ValidationError('La unidad no existe en el grupo')
       
        fecha = datetime.datetime.strptime(codigo[13:21], '%Y%m%d').date()
        
        if datetime.date.today() != fecha:
            raise forms.ValidationError('El enrolamiento no es del día de hoy')

        sedes_hoy = m.Sede.objects.filter(fecha=datetime.date.today(), unidades=unidad)

        if not sedes_hoy:
            raise forms.ValidationError('La unidad no está habilitada para enrolamiento')

        return codigo
    
    def clean_recibo_inicio(self):
        return validar_recibo(self.cleaned_data['recibio_inicio'])
    
    def clean_recibo_final(self):
        return validar_recibo(self.cleaned_data['recibo_final'])

    def save(self, commit=True):
        """ Añade la información de la estación en la sede """
        
        recibo_inicio = self.cleaned_data['recibo_inicio']
        recibo_final = self.cleaned_data['recibo_final']
        unidad = m.Unidad.objects.get(kit=recibo_inicio[:4])
        nuevo_enrol = m.Enrolamiento(recibo_inicio=recibo_inicio, recibo_final=recibo_final)
        nuevo_enrol.unidad = unidad
        nuevo_enrol.sede = m.Sede.objects.get(fecha=datetime.date.today(), unidades=unidad)

        if commit:
            nuevo_enrol.save()

        return nuevo_enrol
