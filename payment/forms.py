from django import forms
from .models import ShippingAddress

#formulario para modificar los datos de envio
class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields =[ "shipping_full_name",  "shipping_address1", "shipping_city", "shipping_state", "shipping_zipcode",  "shipping_country","shipping_email"]
        
        exclude = ["user",] 
        
# formulario de pagoNO TEGO QUE GUARDARLO EN MY BASE DE DATOS POR TEMAS LEGALES ESTOS E MANDA STRIKE ESE SE ENCARGA DE REALIZARLO 
class PaymentForm(forms.Form):
    # Nombre en la tarjeta
    card_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre en la tarjeta'}), required=True)
    
    # Número de la tarjeta
    card_number = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de la tarjeta'}), required=True)
    
    # Fecha de expiración de la tarjeta
    card_exp_date = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fecha de expiración'}), required=True)
    
    # Código CVV de la tarjeta
    card_cvv_number = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código CVV'}), required=True)
    
    # Dirección de facturación (línea 1)
    card_address1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección de facturación 1'}), required=True)
    
    # # Dirección de facturación (línea 2, opcional)
    # card_address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección de facturación 2'}), required=False)
    
    # Ciudad de facturación
    card_city = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad de facturación'}), required=True)
    
    # Estado o provincia de facturación
    card_state = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado o provincia'}), required=True)
    
    # Código postal de facturación
    card_zipcode = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código postal'}), required=True)
    
    # País de facturación
    card_country = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País de facturación'}), required=True)