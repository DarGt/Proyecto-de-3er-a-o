from django import forms
from .models import Producto, Perdida, CantidadPerdida, DetalleProveedor

class ProductosForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'precio_venta', 'coste', 'fecha_de_ingreso', 'existencia',
            'descripcion', 'id_estado_producto', 'id_clase', 'id_clase2', 'id_clase3',
            'imagen1', 'imagen2', 'imagen3', 'imagen4', 'is_sale'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'coste': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_de_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'existencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'id_estado_producto': forms.Select(attrs={'class': 'form-select'}),
            'id_clase': forms.Select(attrs={'class': 'form-select'}),
            'id_clase2': forms.Select(attrs={'class': 'form-select'}),
            'id_clase3': forms.Select(attrs={'class': 'form-select'}),
            'imagen1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'imagen2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'imagen3': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'imagen4': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class PerdidaForm(forms.ModelForm):
    class Meta:
        model = Perdida
        fields = ['fecha', 'total', 'id_estado', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control'}),
            'id_estado': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CantidadPerdidaForm(forms.ModelForm):
    class Meta:
        model = CantidadPerdida
        fields = ['costo_unitario', 'cantidad', 'id_producto', 'id_perdida']
        widgets = {
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'id_producto': forms.Select(attrs={'class': 'form-select'}),
            'id_perdida': forms.Select(attrs={'class': 'form-select'}),
        }

class DetalleProveedorForm(forms.ModelForm):
    class Meta:
        model = DetalleProveedor
        fields = ['nombre', 'direccion', 'telefono', 'correo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }
