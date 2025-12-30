from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import  UserCreationForm
from accounts.models import Usuario


class Registro_de_usuario(UserCreationForm):
    email = forms.EmailField(label="Correo electronico")
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    
    class Meta:
        model = User
        fields =["username", "email", "first_name", "last_name",  "password1", "password2" ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar mensajes de ayuda
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
    
    def clean_email(self):
        email_field = self.cleaned_data["email"]
        if User.objects.filter(email = email_field).exists():
            raise forms.ValidationError("El correo electronico ya esta registrado")
        
        return email_field
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields=["first_name", "last_name"]

#clas que me permite modificar datos
class UsuarioleForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields =["image", "address", "location", "city", "state", "zipcode", "telephone", "country"]


#formulario de nuevo usuario desde admin

class NuevoUsuarioAdmin(forms.ModelForm):
    class Meta:
        model = User
        fields=["username","first_name", "last_name", "email"]


