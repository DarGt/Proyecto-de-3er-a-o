from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic.base import TemplateView
from django.contrib.auth.models import Group
from django.views import View
from .forms import Registro_de_usuario, UserForm,UsuarioleForm, NuevoUsuarioAdmin
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin , LoginRequiredMixin
import os
from django.conf import settings
from django.contrib.auth.models import User#import
from django.core.paginator import Paginator
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth import update_session_auth_hash
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from guardar.models import  Producto , Clase

from django.views.generic import ListView
from django.db.models import Q
from accounts.models import Usuario
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress

from payment.models import Order, OrderItem
from .models import Comentario

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from datetime import date, timedelta
from accounts.models import EstadoCuentaUsuario 

# Create your views here.

@csrf_exempt
@login_required
def like_toggle(request, id_producto):
    if request.method == 'POST':
        try:
            producto = Producto.objects.get(id_producto=id_producto)
            usuario_obj = Usuario.objects.get(user=request.user)
        except (Producto.DoesNotExist, Usuario.DoesNotExist):
            return JsonResponse({'error': 'Producto o usuario no encontrado.'}, status=404)

        from .models import Like
        like_obj = Like.objects.filter(producto=producto, usuario=usuario_obj).first()
        if like_obj:
            like_obj.delete()
            liked = False
        else:
            Like.objects.create(producto=producto, usuario=usuario_obj)
            liked = True
        likes_count = Like.objects.filter(producto=producto).count()
        return JsonResponse({'liked': liked, 'likes_count': likes_count})
    return JsonResponse({'error': 'Método no permitido.'}, status=405)
def plural_to_singular(plural):
    plural_singular ={
        "usuarios":"usuario",
        "caja":"caja",
        "almacen":"almacen",
        "administrativos":"administrativo",
    }
    return plural_singular.get(plural, "error")
#octener usuario , color grupo
def get_group_and_color(user):
    grupo = user.groups.first()
    grupo_id = None
    nombre_d_grupo = None
    group_name_singular = None
    color = None
    if grupo:
            if grupo.name == "usuarios":
                color = "bg-primary"
            elif grupo.name == "caja":
                color = "bg-success"
            elif grupo.name == "almacen":
                color = "bg-secondary"
            elif grupo.name == "administrativos":
                color = "bg-danger"
            
            grupo_id = grupo.id
            nombre_d_grupo = grupo.name
            group_name_singular = plural_to_singular(grupo.name)
    return grupo_id, nombre_d_grupo, group_name_singular, color



#decorador permite reutilizarlo 
def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch
    
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        
        grupo_id, nombre_d_grupo, group_name_singular, color = get_group_and_color(user)
        context = {
            "nombre_d_grupo": nombre_d_grupo,
            "group_name_singular": group_name_singular,
            "color": color
        }
        
        self.extra_context = context
        return original_dispatch(self, request, *args, **kwargs)
    
    view_class.dispatch = dispatch
    return view_class


@add_group_name_to_context
class Principal(TemplateView):
    template_name = 'index.html'
    
#pagina de  informacion
@add_group_name_to_context
class Informacion(TemplateView):
    template_name = 'informacion.html'


#!pagina para errores de nivel de usuario
@add_group_name_to_context
class Error_Permiso(TemplateView):
    template_name = "error.html"
    
    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        error_imagen_path = os.path.join(settings.MEDIA_URL, "error.png")
        contex["error_imagen_path"] = error_imagen_path
        return contex

#registro usuario 
class Registro(View):
    def get(self, request):
        data = {
            "formulari_registro": Registro_de_usuario()
        }
        return render(request, "registration/register.html", data)
    
    def post(self, request):
        user_crea_formulatio = Registro_de_usuario(data=request.POST)
        if user_crea_formulatio.is_valid():
            user_crea_formulatio.save()
            user = authenticate(username=user_crea_formulatio.cleaned_data["username"], password=user_crea_formulatio.cleaned_data["password1"])
            login(request, user)

            # Después de iniciar sesión, cargamos el carrito del usuario
            current_user = Usuario.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart

            if saved_cart:
                # Si tiene carrito guardado, convertir el JSON a un diccionario
                converted_cart = json.loads(saved_cart)
                # Cargar el diccionario en la sesión del carrito
                cart = Cart(request)
                for key, value in converted_cart.items():
                    cart.add(product_id=key, quantity=value)
            
            messages.success(request, "Inicio de sesión exitoso")
            return redirect("index")
        
        data = {
            "formulari_registro": user_crea_formulatio
        }
        return render(request, "registration/register.html", data)

def cerrar_sesion(request):
    logout(request)
    messages.success( request,("Cerro sesión de forma correcta"))
    return redirect("index")

#perfi
@add_group_name_to_context
class PerfilView(TemplateView):
    template_name = "profile/perfiles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user_form"] = UserForm(instance=user)
        context["profile_form"] = UsuarioleForm(instance=user.profile)
        context["shipping_form"] = ShippingForm()  # Agregar ShippingForm al contexto
        
        try:
            estado = user.estado_cuenta
            context["solicitud_eliminacion"] = estado.solicitar_eliminacion
        except EstadoCuentaUsuario.DoesNotExist:
            context["solicitud_eliminacion"] = False
            
        # Contador de pedidos no enviados para administradores 
        pending_orders_count = Order.objects.filter(shipped=False).count()
        context["pending_orders_count"] = pending_orders_count
        
        # Contador de productos por agotarse (existencia <= 5)
        low_stock_count = Producto.objects.filter(existencia__lte=5).count()
        context["low_stock_count"] = low_stock_count
        
        # Contador de pedidos no enviados SOLO del usuario actual
        user_pending_orders_count = Order.objects.filter(user=user, shipped=False).count()
        context["user_pending_orders_count"] = user_pending_orders_count
        
        # Contador de usuarios que han solicitado eliminación
        context["estado_cuenta_count"] = EstadoCuentaUsuario.objects.filter(solicitar_eliminacion=True).count()

        # Funcionalidades específicas por usuario
        if user.groups.first().name == "administrativos":
            # Obtengo todos los usuarios que no sean admin
            admin_group = Group.objects.get(name="administrativos")
            all_users = User.objects.exclude(groups__in=[admin_group])
            # Obtengo los grupos
            all_groups = Group.objects.all()
            user_profiles = []

            for user in all_users:
                profile = user.profile
                user_groups = user.groups.all()
                user_profiles.append({
                    "user": user,
                    "groups": user_groups,
                    "profile": profile
                })
            

            # Aplico paginación
            paginator = Paginator(user_profiles, 6)  # 10 perfiles por página
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            

            context["page_obj"] = page_obj
            context["all_groups"] = all_groups

        return context

    #parte que paso el formulario para editar datos
    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type")  # Identificar el formulario enviado

        if form_type == "user_form":  # Formulario de perfil
            user = self.request.user
            
            user_form = UserForm(request.POST, instance=user)
            profile_form = UsuarioleForm(request.POST, request.FILES, instance=user.profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect("perfil")
            else:
                messages.error(request,"Error de tipo:",shipping_form.errors, "AL momento de actualizar")

            context = self.get_context_data()
            context["user_form"] = user_form
            context["profile_form"] = profile_form
            return render(request, "profile/perfiles.html", context)

        elif form_type == "shipping_form":  # Formulario de dirección de envío
            
            user = self.request.user
            # Obtén la dirección de envío existente o crea una nueva
            shipping_address, created = ShippingAddress.objects.get_or_create(user=user) 
            shipping_form = ShippingForm(request.POST, instance=shipping_address)

            if shipping_form.is_valid():
                
                shipping_form.save()
                messages.success(request, "Información de envío actualizada correctamente.")
                return redirect("perfil")
            else:
                messages.error(request,"Error de tipo:",shipping_form.errors, "AL momento de actualizar")
                
                context = self.get_context_data()
                context["shipping_form"] = shipping_form
                return render(request, "profile/perfiles.html", context)
                
            
        # Nueva rama para solicitud de eliminación de cuenta
        elif request.POST.get("delete_request") == "true":
                user = request.user
                motivo = request.POST.get("motivoBorrado", "")
                try:
                    estado = user.estado_cuenta
                except EstadoCuentaUsuario.DoesNotExist:
                    estado = EstadoCuentaUsuario(user=user)
                estado.solicitar_eliminacion = True
                estado.motivo_borrado = motivo
             # fecha_solicitud se asigna automáticamente en el save()
                estado.save()
                messages.success(request, "¡Solicitud de eliminación enviada correctamente!")
                return redirect("perfil")
        elif request.POST.get("cancel_delete_request") == "true":
            user = request.user
            try:
                estado = user.estado_cuenta
                estado.delete()  # Elimina el registro de EstadoCuentaUsuario
                messages.success(request, "¡Solicitud de eliminación cancelada correctamente!")
            except EstadoCuentaUsuario.DoesNotExist:
                pass
            return redirect("perfil")


    
    
    
#cambiar contraseña
@add_group_name_to_context
class CambioContraseña(PasswordChangeView):
    template_name = "password.html"
    success_url = reverse_lazy("perfil")
    
    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex["password_changed"] = self.request.session.get("password_chaged", False)
        return contex
    
    def from_valid(self, form):
        messages.success(self.request, "Cambio de contraseña exitoso")
        update_session_auth_hash(self.request, form.user)
        self.request.session["password_changed"] = True
        return super().form_valid(form)
    
    def from_invalid(self, form):
        messages.success(self.request, "No se pudo cambiar la contraseña, intente nuevamente")
        return super().from_invalid(form)
    
#visualizacionde perfil de un usuario
@add_group_name_to_context
class Detalles_Usuario_admin(LoginRequiredMixin,DetailView):
    model = User
    template_name = "user_detail.html"
    context_object_name ="user_profile"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        grupo_id, nombre_d_grupo, group_name_singular, color = get_group_and_color(user)
        
        #octengo todos los grupos
        groups = Group.objects.all()
        singular_name = [plural_to_singular(group.name).capitalize() for group in groups]

        groups_id = [group.id for group in groups]
        singular_groups = zip(singular_name, groups_id)
        context["singular_groups"] = singular_groups
        context["grupo_id_user"] = grupo_id
        context["nombre_d_grupo_usuarios"]= nombre_d_grupo
        context["group_name_singular_usuarios"]= group_name_singular
        context["color_usuarios"]= color
        
        return context
#grabar datos de un usuario desde admin
def superuser_edit(request, user_id):
    if not request.user.is_superuser:
        return redirect("error")
    user = User.objects.get(pk=user_id)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = UsuarioleForm(request.POST, request.FILES, instance=user.profile)
        group = request.POST.get("group")
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            user.groups.clear()#borro los grupos para adicionarlo a un nuevo grupo
            user.groups.add(group)
            return redirect("user_detail", pk=user.id)
    else :
        user_form = UserForm(instance=user)
        profile_form = UsuarioleForm(instance=user.profile)
        
    context = {
        "user_form": user_form,
        "profile_form":profile_form
    }
    return render(request,"user_detail.html", context)

#agregar usuario desde admin
@add_group_name_to_context
class AddUserview(UserPassesTestMixin, LoginRequiredMixin,CreateView):#!UserPassesTestMixin, LoginRequiredMixin para inperdir que un usuario o caja o almacen accedan a esto
    model = User
    form_class = NuevoUsuarioAdmin
    template_name = "agregar_usuario.html"
    success_url = "/perfil/"
    
    def test_func(self):
        #return self.request.user.is_superuser or self.request.user.is_staff #si est trabajador o admin
        return self.request.user.is_superuser#!solo usuarios administrativos pueden acceder
        #redirijoa pagina de error
    def handle_no_permission(self):
        return redirect("error")#http://127.0.0.1:8000/agregar_usuario/
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = Group.objects.all()
        singular_groups = [plural_to_singular(group.name).capitalize() for group in groups]
        context["groups"] = zip(groups, singular_groups)
        return context
    
    def form_valid(self, form):
        # Obtengo el grupo seleccionado
        group_id = self.request.POST["group"]
        group = Group.objects.get(id=group_id)
        
        # Crear usuario sin guardar todavía
        user = form.save(commit=False)
        # Crear una contraseña predeterminada
        user.set_password("contraseña")
        
        # Dar permisos de staff si el grupo no es "Usuario" (ID = 1)
        if group_id != "1":
            user.is_staff = True
        
        # Guardar usuario
        user.save()
        
        # Asignar grupo al usuario
        user.groups.clear()
        user.groups.add(group)
        messages.success(self.request, "Usuario Creado con exito recuende la contraseña es !contraseña!.")
        return super().form_valid(form)

    
@login_required
def eliminar_usuario(request, user_id):
    # Verifica si el usuario actual tiene permisos
    if request.user.id != user_id and not request.user.is_superuser:
        return redirect("error")  # Redirige si no tiene permisos

    user = get_object_or_404(User, pk=user_id)
    user.delete()  # Elimina al usuario

    # Agregar mensaje de éxito
    messages.success(request, "¡Usuario eliminado exitosamente!")

    return redirect("perfil")  # Redirige al perfil después de eliminar

#!!!agregaods
#pagina de carrito
@add_group_name_to_context
class Carrito(TemplateView):
    template_name = 'carrito.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        if query:
            # Filtrar productos por nombre o descripción que contengan el término de búsqueda
            productos = Producto.objects.filter(
                Q(nombre__icontains=query) | Q(descripcion__icontains=query),
                id_estado_producto=1,
                 existencia__gte=1  # Filtrar productos con existencia de al menos 1
            ).order_by('nombre')
        else:
            # Obtener todos los productos por estado de producto 1 y ordenarlos
            productos = Producto.objects.filter(id_estado_producto=1,existencia__gte=1).order_by('nombre')
        
        # Configurar el paginador para 12 productos por página
        paginator = Paginator(productos, 12)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Añadir los productos paginados al contexto
        context['products'] = page_obj

        # Añadir una variable para indicar si no se encontraron productos
        context['no_products'] = not productos.exists()

        clases = Clase.objects.all()
        
        # Añadir las categorías al contexto
        context['clases'] = clases
        context['query'] = query

        # Lógica de likes
        from .models import Like
        usuario_like = None
        if self.request.user.is_authenticated:
            try:
                usuario_like = Usuario.objects.get(user=self.request.user)
            except Usuario.DoesNotExist:
                usuario_like = None
        likes_dict = {}
        user_likes = set()
        for producto in page_obj:
            likes_count = Like.objects.filter(producto=producto).count()
            likes_dict[producto.id_producto] = likes_count
            if usuario_like:
                if Like.objects.filter(producto=producto, usuario=usuario_like).exists():
                    user_likes.add(producto.id_producto)
        context['likes_dict'] = likes_dict
        context['user_likes'] = user_likes

        return context
    


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q


@login_required
@csrf_exempt
def agregar_comentario(request, id_producto):
    user = request.user
    producto = Producto.objects.get(id_producto=id_producto)
    try:
        usuario_obj = Usuario.objects.get(user=user)
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no válido.")
        return redirect('producto_detail', pk=id_producto)

    ha_comprado = OrderItem.objects.filter(
        order__user=user,
        product=producto,
        order__recibido=True
    ).exists()

    if not ha_comprado:
        messages.error(request, "Solo puedes comentar productos que hayas comprado y recibido.")
        return redirect('producto_detail', pk=id_producto)

    ya_comento = Comentario.objects.filter(
        producto=producto,
        usuario=usuario_obj
    ).first()

    if ya_comento:
        messages.warning(request, "Ya has comentado este producto. Puedes editar tu comentario.")
        return redirect('producto_detail', pk=id_producto)

    if request.method == "POST":
        texto = request.POST.get("texto")
        calificacion = int(request.POST.get("calificacion"))
        Comentario.objects.create(
            producto=producto,
            usuario=usuario_obj,
            texto=texto,
            calificacion=calificacion
        )
        messages.success(request, "Comentario agregado correctamente.")
    return redirect('producto_detail', pk=id_producto)





@login_required
@csrf_exempt
def editar_comentario(request, id_producto):
    user = request.user
    producto = Producto.objects.get(id_producto=id_producto)
    try:
        usuario_obj = Usuario.objects.get(user=user)
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no válido.")
        return redirect('producto_detail', pk=id_producto)

    comentario = Comentario.objects.filter(
        producto=producto,
        usuario=usuario_obj
    ).first()

    if not comentario:
        messages.error(request, "No tienes comentarios para editar en este producto.")
        return redirect('producto_detail', pk=id_producto)

    if request.method == "POST":
        comentario.texto = request.POST.get("texto")
        comentario.calificacion = int(request.POST.get("calificacion"))
        comentario.save()
        messages.success(request, "Comentario actualizado correctamente.")
        return redirect('producto_detail', pk=id_producto)

    comentarios = Comentario.objects.filter(producto=producto).order_by('-fecha')
    clases = Clase.objects.all()

    context = {
        "producto": producto,
        "comentarios": comentarios,
        "categories": clases,
        "comentario_usuario": comentario,
        "modo_edicion": True  #  Bandera para el template
    }

    return render(request, "producto.html", context)



@login_required
def eliminar_comentario(request, id_producto):
    user = request.user
    producto = Producto.objects.get(id_producto=id_producto)
    try:
        usuario_obj = Usuario.objects.get(user=user)
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no válido.")
        return redirect('producto_detail', pk=id_producto)

    comentario = Comentario.objects.filter(
        producto=producto,
        usuario=usuario_obj
    ).first()

    if comentario:
        comentario.delete()
        messages.success(request, "Comentario eliminado.")
    else:
        messages.error(request, "No se encontró tu comentario.")

    return redirect('producto_detail', pk=id_producto)


#pagina del producto
@add_group_name_to_context
class ProductoDetailView(DetailView):
    model = Producto
    template_name = "producto.html"
    context_object_name = "producto"

    def get_object(self, queryset=None):
        try:
            # Usar el campo correcto del modelo para buscar el producto
            producto = Producto.objects.get(id_producto=self.kwargs['pk'])
            return producto
        except Producto.DoesNotExist:
            return None  # Retornar None si no se encuentra el producto

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            producto = self.get_object()
            opciones_cantidad = [1,2,3,4,5,6,12,24,60,100,1000]
            context['opciones_cantidad'] = opciones_cantidad
            context['producto'] = producto

            if not producto:
                context['error'] = "Producto no encontrado"
            else:
                if producto.id_clase:
                    context['categoria'] = producto.id_clase
                    context['subcategorias'] = producto.id_clase.subclase_set.all()

                productos_relacionados = Producto.objects.filter(
                    id_clase=producto.id_clase
                ).exclude(id_producto=producto.id_producto)[:4]
                context['productos_relacionados'] = productos_relacionados

                comentarios = Comentario.objects.filter(producto=producto).order_by('-fecha')
                context['comentarios'] = comentarios

                if self.request.user.is_authenticated:
                    try:
                        usuario_obj = Usuario.objects.get(user=self.request.user)
                        comentario_usuario = Comentario.objects.filter(
                            producto=producto,
                            usuario=usuario_obj
                        ).first()
                        context['comentario_usuario'] = comentario_usuario
                    except Usuario.DoesNotExist:
                        context['comentario_usuario'] = None

            clases = Clase.objects.all()
            context['categories'] = clases
            return context
    
@add_group_name_to_context
class CategoryListView(ListView):
    model = Producto
    template_name = "categoria.html"
    context_object_name = "products"

    def get_queryset(self):
        # Obtener el valor del parámetro 'foo' de la URL y reemplazar guiones por espacios
        foo = self.kwargs.get('foo', '').replace("-", " ")
        query = self.request.GET.get('q', '')

        try:
            # Buscar la subclase por su nombre
            subclase = Clase.objects.get(nombre_clase=foo)
            if query:
                # Filtrar productos por nombre o descripción que contengan el término de búsqueda
                return Producto.objects.filter(
                    Q(nombre__icontains=query) | Q(descripcion__icontains=query),
                    id_clase=subclase.id_clase
                ).order_by('nombre')
            else:
                # Filtrar productos que pertenecen a la subclase encontrada y ordenarlos
                return Producto.objects.filter(id_clase=subclase.id_clase).order_by('nombre')
        except Clase.DoesNotExist:
            # Retornar un queryset vacío si no se encuentra la subclase
            return Producto.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener el valor del parámetro 'foo' para obtener la subclase
        foo = self.kwargs.get('foo', '').replace("-", " ")
        query = self.request.GET.get('q', '')

        try:
            subclase = Clase.objects.get(nombre_clase=foo)
            context['subclase'] = subclase
        except Clase.DoesNotExist:
            # Manejo de errores en el contexto
            messages.error(self.request, "La categoría de producto no está disponible o no existe.")
            return redirect("carrito")  # Redirigir a una página predeterminada en caso de error

        # Añadir las categorías al contexto
        clases = Clase.objects.all()
        context['categories'] = clases
        context['query'] = query

        return context

#logica para realizar crear el buscado de la tienda depues xd
@add_group_name_to_context
class CategorySummaryView(TemplateView):
    template_name = "cart/category_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aquí puedes agregar información adicional al contexto si es necesario
        context["categories"] =  Clase.objects.all()
        
        return context

#busqueda de productos
def search(request):
    return render(request, "search.html",{})
    

@add_group_name_to_context
class CustomLoginView(LoginView):
    template_name = "registration/inisio.html"

    def form_valid(self, form):
        # Lógica de inicio de sesión
        response = super().form_valid(form)
        
        # Cargar el carrito guardado del usuario
        current_user = Usuario.objects.get(user__id=self.request.user.id)
        saved_cart = current_user.old_cart
        print("hola")
        if saved_cart:
            # Si tiene carrito guardado, convertir el JSON a un diccionario
            converted_cart = json.loads(saved_cart)
            # Cargar el diccionario en la sesión del carrito
            cart = Cart(self.request)
            for key, value in converted_cart.items():
                cart.db_add(product=key, quantity=value)
        
        # Verificar si el usuario es admin o staff
        if self.request.user.is_superuser or self.request.user.is_staff:
            messages.success(self.request, "Inicio de sesión exitoso. ¡Bienvenido!")
            return redirect("perfil")  # Redirige al perfil
        else:
            messages.success(self.request, "Inicio de sesión exitoso. ¡Bienvenido!")
            return redirect("index")  # Redirige al índice

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error, por favor intente nuevamente.")
        return super().form_invalid(form)
    
    
@add_group_name_to_context
class LoginUserView(View):
    template_name = 'registration/ini.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Manejo del carrito guardado
            current_user = Usuario.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart
            if saved_cart:
                # Convertir el carrito guardado en un diccionario
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            # Redirigir según el tipo de usuario
            if request.user.is_superuser or request.user.is_staff:
                messages.success(request, "Inicio de sesión exitoso. ¡Bienvenido!")
                return redirect('perfil')  # Redirige al perfil
            else:
                messages.success(request, "Inicio de sesión exitoso. ¡Bienvenido!")
                return redirect('index')  # Redirige al índice
        else:
            messages.error(request, "Hubo un error, por favor intente nuevamente.")
            return redirect('ini')
#contador para ver si hay ordenes 
def administrativos(request):
    # Contar los pedidos no enviados
    pending_orders_count = Order.objects.filter(shipped=False).count()

    # Obtener los pedidos no enviados
    pending_orders = Order.objects.filter(shipped=False)

    # Pasar los pedidos pendientes y el contador al contexto
    print(pending_orders_count)
    return render(request, 'profile/perfiles.html', {
        'pending_orders': pending_orders,
        'pending_orders_count': pending_orders_count
    })
    
#funciones para el cmabio de contraseña con correo
@add_group_name_to_context
class PasswordResetView(TemplateView):
    template_name = 'registration/password_reset_forms.html'
@add_group_name_to_context
class PasswordResetDoneView(TemplateView):
    template_name = 'registration/password_reset_done.html'
@add_group_name_to_context
class PasswordResetConfirmView(TemplateView):
    template_name = 'registration/password_reset_confirms.html'
@add_group_name_to_context
class PasswordResetCompleteView(TemplateView):
    template_name = 'registration/password_reset_complete.html'
    
#funcion para eliminar usuario por solicitud de usuario
@add_group_name_to_context
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class EliminaUsuario2View(TemplateView):
    template_name = 'elimina_user_admin_2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtrar solo los estados de cuenta con solicitud de eliminación
        estados = EstadoCuentaUsuario.objects.filter(solicitar_eliminacion=True)
        usuarios_a_eliminar = []
        for estado in estados:
            usuario = estado.user
            usuarios_a_eliminar.append({
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "motivo_borrado": estado.motivo_borrado,
                "fecha_solicitud": estado.fecha_solicitud,
                "puede_eliminarse": estado.puede_eliminarse,
            })
        context["usuarios_a_eliminar"] = usuarios_a_eliminar
        return context

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        if user_id:
            return eliminar_usuario(request, user_id)
        return redirect("perfil")
    
    