from django.contrib import admin
from django.urls import path, include
from guardar import views 
from django.conf import settings
from django.contrib.staticfiles.urls import static
from guardar.views import GenerarPDFView, ProductosPorAgotarseView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import GenerarPDFUsuarioView, GenerarPDFUsuariosAdminView
from django.conf.urls.static import static
from accounts.views import UserListAPI, UsuarioDetailAPI
from payment.views import GenerarPDFReciboView
from guardar.views import ProductoListAPI, ProductoDetailAPI, api_registrar_venta
from core.views import OrderSerializerAPI
#Importaciones para la documentación de la API
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="API Ferretería",
      default_version='v1',
      description="Documentación oficial de la API para la App Móvil",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="tuemail@ferreteria.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,), # Permitimos que cualquiera vea la doc (por ahora)
)
urlpatterns = [
     # --- NUEVAS RUTAS DE AUTENTICACIÓN ---
    # Esta es la ruta para hacer "Login" y recibir el token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Esta es para refrescar el token cuando caduca (avanzado, pero bueno tenerla)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     
     #Api ruta prueba
     path('api/productos/', ProductoListAPI.as_view(), name='api_productos_list'),
     path('api/usuarios/', UserListAPI.as_view(), name='api_usuarios_list'),
     path('api/ordenes/', OrderSerializerAPI.as_view(), name='api_ordenes_list'),
     
     #rutas para la documentación de la API
     path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
     path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

     # urls.py
     path('api/productos/<int:id_producto>/', ProductoDetailAPI.as_view(), name='api_productos_detail'),
     path('api/usuarios/<int:id_usuario>/', UsuarioDetailAPI.as_view(), name='api_usuarios_detail'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('cart/', include('cart.urls')),
    path('payment/', include('payment.urls')),
    
    path('recibo/pdf/<int:pk>/', GenerarPDFReciboView.as_view(), name='generar_pdf_recibo'),
    path('pdf/usuario/', GenerarPDFUsuarioView.as_view(), name='pdf_usuario'),

    path('pdf/usuario/<int:usuario_id>/',
         GenerarPDFUsuarioView.as_view(), name='pdf_usuario_id'),

    path('pdf/usuarios/', GenerarPDFUsuariosAdminView.as_view(),
         name='pdf_usuarios_admin'),

    path('buscar/productos', views.BusquedaProductosView.as_view(),
         name="busqueda_productos"),
    path('productos', views.IndexView.as_view(), name='productos'),
    path('crear/productos', views.CrearProductosView.as_view(), name='crear_productos'),
    path('editar/productos/<int:producto_id>/',
         views.EditarProductosView.as_view(), name='editar_productos'),
    path('detalles/productos', views.DetallesProductoView.as_view(),
         name='detalles_productos'),
    path('sugerir_eliminacion/<int:producto_id>/',
         views.SugerirEliminacionView.as_view(), name='sugerir_eliminacion'),
    path('eliminar/<int:id>', views.EliminarProductosView.as_view(), name='eliminar'),
    path('productos/pdf/', GenerarPDFView.as_view(), name='generar_pdf'),
    path('productos-por-agotarse/', ProductosPorAgotarseView.as_view(), name='productos_por_agotarse'),
    path('perdidas/', views.PerdidaListView.as_view(), name='perdida_list'),
    path('perdidas/nueva/', views.PerdidaCreateView.as_view(), name='perdida_create'),
    path('cantidadperdida/', views.CantidadPerdidaListView.as_view(), name='cantidadperdida_list'),
    path('cantidadperdida/nueva/', views.CantidadPerdidaCreateView.as_view(), name='cantidadperdida_create'),
    
    # ... tus otras rutas ...
    
    # Ruta NUEVA exclusiva para la App Móvil (devuelve JSON, no HTML)
    path('api/movil/productos/', views.api_productos_flutter, name='api_productos_movil'),
    path('api/crear_venta/', api_registrar_venta, name='api_crear_venta'),
    path('api/mis_compras/', views.api_mis_compras, name='api_mis_compras'),
    path('api/usuario/', views.api_datos_usuario, name='api_datos_usuario'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)