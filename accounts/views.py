from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.templatetags.static import static
from weasyprint import HTML
from .models import Usuario
from .serializers import usuarioSerializer
from rest_framework import generics
# Create your views here.


def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch

    def dispatch(self, request, *args, **kwargs):
        # Aquí puedes añadir lógica común si es necesario
        # Cambiar view_class por self
        return original_dispatch(self, request, *args, **kwargs)

    view_class.dispatch = dispatch
    return view_class




@method_decorator(login_required, name='dispatch')
class GenerarPDFUsuarioView(View):
    def get(self, request, *args, **kwargs):
        usuario = request.user
        # construir URLs absolutas para que WeasyPrint pueda resolver las imágenes
        logo_url = request.build_absolute_uri(static('logo/LogoFerrer.png'))
        # avatar: si el usuario tiene imagen en media, crear URL absoluta; si no, usar imagen por defecto estática
        if hasattr(usuario, 'profile') and usuario.profile.image and getattr(usuario.profile.image, 'url', None):
            try:
                avatar_path = usuario.profile.image.url
            except Exception:
                avatar_path = None
        else:
            avatar_path = None

        if avatar_path:
            avatar_url = request.build_absolute_uri(avatar_path)
        else:
            avatar_url = request.build_absolute_uri(static('img/default-user.png'))

        html_string = render_to_string(
            'Usuarios/pdf_usuario.html', {'usuario': usuario, 'logo_url': logo_url, 'avatar_url': avatar_url})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{usuario.username}_perfil.pdf"'
        # pasar base_url para resolución de recursos relativos si hiciera falta
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
        return response

@add_group_name_to_context
class UserListAPI(generics.ListCreateAPIView):
    
    queryset = Usuario.objects.all()
    serializer_class = usuarioSerializer
@add_group_name_to_context
class UsuarioDetailAPI(generics.RetrieveUpdateDestroyAPIView): # <--- Cambio aquí
    queryset = Usuario.objects.all()
    serializer_class = usuarioSerializer
    lookup_field = 'id_usuario'

@add_group_name_to_context
class GenerarPDFUsuariosAdminView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        # Verificar si el usuario es administrador
        if not request.user.is_staff:
            messages.error(
                request, "No tienes permiso para acceder a esta página.")
            return redirect('home')

        # Obtener todos los usuarios
        usuarios = Usuario.objects.all()

        # Renderizar el contenido HTML
        html_string = render_to_string(
            'Usuarios/pdf_usuarios_admin.html', {'usuarios': usuarios})

        # Generar el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="usuarios.pdf"'
        HTML(string=html_string).write_pdf(response)

        return response
