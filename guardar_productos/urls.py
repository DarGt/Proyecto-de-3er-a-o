from django.contrib import admin
from django.urls import path, include
from guardar import views 
from django.conf import settings
from django.contrib.staticfiles.urls import static
from guardar.views import GenerarPDFView, ProductosPorAgotarseView

from accounts.views import GenerarPDFUsuarioView, GenerarPDFUsuariosAdminView
from django.conf.urls.static import static
from accounts.views import UserListAPI
from payment.views import GenerarPDFReciboView
from guardar.views import ProductoListAPI
urlpatterns = [
     
     #Api ruta prueba
     path('api/productos/', ProductoListAPI.as_view(), name='api_productos_list'),
     path('api/usuarios/', UserListAPI.as_view(), name='api_usuarios_list'),
     
     
     
     
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
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)