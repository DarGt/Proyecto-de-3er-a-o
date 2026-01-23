from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import ProductosForm, PerdidaForm, CantidadPerdidaForm, DetalleProveedorForm
from .models import Producto, SugerenciaEliminacion, Perdida, CantidadPerdida, DetalleProveedor, Venta, DetalleVenta
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from core.views import add_group_name_to_context
from django.contrib.auth.mixins import UserPassesTestMixin
from django.templatetags.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, permissions, filters
from .serializers import ProductoSerializer, VentaSerializer, DetalleVentaSerializer
from django.db import transaction # Vital para evitar errores de dinero/stock



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_registrar_venta(request):
    data = request.data
    items = data.get('items', []) # Flutter envía: [{'id': 1, 'cantidad': 2}, ...]
    total_venta = data.get('total', 0)

    if not items:
        return Response({"error": "El carrito está vacío"}, status=400)

    try:
        with transaction.atomic():
            # 1. Crear la Venta
            venta = Venta.objects.create(
                usuario=request.user, # Usa el usuario logueado (token)
                total=total_venta
            )

            # 2. Procesar cada producto
            for item in items:
                # OJO: Flutter envía 'id', pero tu modelo usa 'id_producto'
                prod_id = item['id'] 
                cantidad = item['cantidad']

                # Bloqueo de base de datos para evitar errores de concurrencia
                producto = Producto.objects.select_for_update().get(pk=prod_id)

                # 3. Validar Stock (Usando tu campo 'existencia')
                if producto.existencia < cantidad:
                    raise Exception(f"Stock insuficiente para {producto.nombre}. Disponibles: {producto.existencia}")

                # 4. Restar Stock
                producto.existencia -= cantidad
                producto.save()

                # 5. Guardar Detalle (Usando tu campo 'precio_venta')
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta,
                    subtotal=producto.precio_venta * cantidad
                )

            return Response({"mensaje": "Venta exitosa", "id_venta": venta.id_venta}, status=200)

    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_mis_compras(request):
    # Filtramos solo las ventas del usuario logueado (request.user)
    # .order_by('-fecha') hace que salgan las más nuevas primero
    ventas = Venta.objects.filter(usuario=request.user).order_by('-fecha')
    serializer = VentaSerializer(ventas, many=True)
    return Response(serializer.data)
@add_group_name_to_context
class ProductoListAPI(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    # 2. Configurar permisos específicos para esta vista
    # IsAuthenticatedOrReadOnly: 
    #   - Si vienes a LEER (Get): Pasa, no importa quién seas.
    #   - Si vienes a ESCRIBIR (Post): Identifícate primero.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Motor de busqueda
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion',]

@add_group_name_to_context
class ProductoDetailAPI(generics.RetrieveUpdateDestroyAPIView): # <--- Cambio aquí
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    lookup_field = 'id_producto'
    permission_classes = [permissions.IsAdminUser]


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # Solo con Token
def api_productos_flutter(request):
    # Buscamos todos los productos
    productos = Producto.objects.all()
    # Usamos tu serializer existente para convertirlos a JSON
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)

class AdminOrAlmacenistaRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.groups.filter(name__in=["almacen", "administrativos"]).exists() or user.is_superuser)
    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a esta página.")
        return redirect('index')

@add_group_name_to_context
class SugerirEliminacionView(View):
    @method_decorator(login_required)
    def get(self, request, producto_id):
        producto = get_object_or_404(Producto, id_producto=producto_id)
        context = {'producto': producto}
        # Agrega el contexto extra manualmente
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        return render(request, 'Productos/sugerir_eliminacion.html', context)

    @method_decorator(login_required)
    def post(self, request, producto_id):
        producto = get_object_or_404(Producto, id_producto=producto_id)
        motivo = request.POST.get('motivo')
        SugerenciaEliminacion.objects.create(
            producto=producto, usuario=request.user, motivo=motivo)
        messages.success(
            request, 'Sugerencia de eliminación enviada al administrador.')
        return redirect('productos')


@add_group_name_to_context
class IndexView(AdminOrAlmacenistaRequiredMixin, TemplateView):
    template_name = 'Productos/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all()
        return context

@add_group_name_to_context
class ProductosView(AdminOrAlmacenistaRequiredMixin, TemplateView):
    template_name = 'Productos/productos.html'

@add_group_name_to_context
class DetallesProductoView(AdminOrAlmacenistaRequiredMixin, TemplateView):
    template_name = 'Productos/detalles_producto.html'

@add_group_name_to_context
class CrearProductosView(AdminOrAlmacenistaRequiredMixin, View):
    @method_decorator(login_required)
    def get(self, request):
        producto_form = ProductosForm()
        context = {'producto_form': producto_form}
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        return render(request, 'Productos/forms.html', context)

    @method_decorator(login_required)
    def post(self, request):
        producto_form = ProductosForm(request.POST, request.FILES)
        context = {'producto_form': producto_form}
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        if producto_form.is_valid():
            producto_form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('productos')
        return render(request, 'Productos/forms.html', context)

@add_group_name_to_context
class EditarProductosView(AdminOrAlmacenistaRequiredMixin, View):
    @method_decorator(login_required)
    def get(self, request, producto_id):
        producto = get_object_or_404(Producto, id_producto=producto_id)
        formulario = ProductosForm(instance=producto)
        context = {'producto_form': formulario}
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        return render(request, 'Productos/forms.html', context)

    @method_decorator(login_required)
    def post(self, request, producto_id):
        producto = get_object_or_404(Producto, id_producto=producto_id)
        formulario = ProductosForm(request.POST, request.FILES, instance=producto)
        context = {'producto_form': formulario}
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        if formulario.is_valid():
            formulario.save()
            return redirect('productos')
        return render(request, 'Productos/forms.html', context)

@add_group_name_to_context
class BusquedaProductosView(TemplateView):
    template_name = 'Paginas/busqueda_produc.html'

@add_group_name_to_context
class EliminarProductosView(AdminOrAlmacenistaRequiredMixin, View):
    @method_decorator(login_required)
    def post(self, request, id):
        producto = get_object_or_404(Producto, id_producto=id)
        producto.delete()
        messages.success(request, "Producto eliminado exitosamente.")
        return redirect('productos')

@add_group_name_to_context
class GenerarPDFView(View):
    def get(self, request, *args, **kwargs):
        productos = Producto.objects.filter(existencia__gt=0)
        # construir URLs absolutas para logo y para las imágenes de cada producto
        logo_url = request.build_absolute_uri(static('logo/LogoFerrer.png'))

        productos_data = []
        for p in productos:
            image_urls = []
            for img_field in ('imagen1', 'imagen2', 'imagen3', 'imagen4'):
                img = getattr(p, img_field, None)
                if img and getattr(img, 'url', None):
                    try:
                        image_urls.append(request.build_absolute_uri(img.url))
                    except Exception:
                        # omitir si no es accesible
                        pass
            productos_data.append({'producto': p, 'images': image_urls})

        html_string = render_to_string(
            'Productos/pdf_template.html', {'productos_data': productos_data, 'logo_url': logo_url})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="productos_en_stock.pdf"'
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
        return response
    
    
@add_group_name_to_context
class ProductosPorAgotarseView(TemplateView):
    template_name = 'profile/productos_por_agotarse.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        LIMITE_STOCK = 5  # Puedes ajustar este valor
        context['productos_agotandose'] = Producto.objects.filter(existencia__lte=LIMITE_STOCK, is_active=True)
        return context

@add_group_name_to_context
class PerdidaListView(TemplateView):
    template_name = 'Productos/perdida_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        context['perdidas'] = Perdida.objects.all()
        return context

@add_group_name_to_context
class PerdidaCreateView(AdminOrAlmacenistaRequiredMixin, View):
    @method_decorator(login_required)
    def get(self, request):
        form = PerdidaForm()
        context = {'form': form}
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        return render(request, 'Productos/perdida_form.html', context)

    @method_decorator(login_required)
    def post(self, request):
        form = PerdidaForm(request.POST)
        context = {'form': form}
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pérdida registrada exitosamente.')
            return redirect('perdida_list')
        return render(request, 'Productos/perdida_form.html', context)

@add_group_name_to_context
class CantidadPerdidaListView(TemplateView):
    template_name = 'Productos/cantidadperdida_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        context['cantidades'] = CantidadPerdida.objects.all()
        return context

@add_group_name_to_context
class CantidadPerdidaCreateView(AdminOrAlmacenistaRequiredMixin, View):
    @method_decorator(login_required)
    def get(self, request):
        form = CantidadPerdidaForm()
        context = {'form': form}
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        return render(request, 'Productos/cantidadperdida_form.html', context)

    @method_decorator(login_required)
    def post(self, request):
        form = CantidadPerdidaForm(request.POST)
        context = {'form': form}
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cantidad de pérdida registrada exitosamente.')
            return redirect('cantidadperdida_list')
        return render(request, 'Productos/cantidadperdida_form.html', context)