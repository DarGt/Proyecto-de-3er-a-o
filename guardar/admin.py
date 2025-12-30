# Esto es lo mas importante del dashboard la mayoria de funciones estan sub cuadradas aqui para un buen funcionamiento ademas de ser el sitio donde agrego funciones nuevas

from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.contrib.import_export.forms import (ExportForm, ImportForm,
                                                SelectableFieldsExportForm)
from unfold.forms import (AdminPasswordChangeForm, UserChangeForm,
                          UserCreationForm)
from import_export import resources, fields
from .models import (
    Clase, EstadoProducto, Producto, SubClase, SugerenciaEliminacion,
    Perdida, CantidadPerdida,  DetalleProveedor, Clase2, Clase3
)
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
import csv
from django.http import HttpResponse
# Register your models here.

admin.site.unregister(User)


@admin.register(Perdida)
class PerdidaAdmin(ModelAdmin):
    list_display = ('id_perdida', 'fecha', 'total', 'id_estado', 'descripcion')
    search_fields = ('descripcion',)
    list_filter = ('fecha', 'id_estado')

@admin.register(CantidadPerdida)
class CantidadPerdidaAdmin(ModelAdmin):
    list_display = ('id_c_perdida', 'id_perdida', 'id_producto', 'cantidad', 'costo_unitario')
    list_filter = ('id_perdida', 'id_producto')


@admin.register(DetalleProveedor)
class DetalleProveedorAdmin(ModelAdmin):
    list_display = ('id_proveedor', 'nombre', 'direccion', 'telefono', 'correo')
    search_fields = ('nombre', 'correo')


    
@admin.register(SugerenciaEliminacion)
class SugerenciaEliminacionAdmin(ModelAdmin):
    list_display = ('producto', 'usuario', 'fecha', 'motivo', 'aceptada')
    actions = ['aceptar_sugerencia']
    list_filter =[('fecha')]
    def aceptar_sugerencia(self, request, queryset):
        for sugerencia in queryset:
            if not sugerencia.aceptada:
                sugerencia.aceptar()
        self.message_user(request, "Las sugerencias seleccionadas han sido aceptadas y los productos eliminados.")
    aceptar_sugerencia.short_description = "Aceptar y eliminar producto sugerido"

@register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Clase)
class ClaseAdmin(ModelAdmin):
    list_display = ('id_clase', 'nombre_clase')
    list_display_links = ('nombre_clase',)


@admin.register(Clase2)
class Clase2Admin(ModelAdmin):
    list_display = ('id_clase2', 'nombre_clase2', 'id_clase')
    list_display_links = ('nombre_clase2',)

@admin.register(Clase3)
class Clase3Admin(ModelAdmin):
    list_display = ('id_clase3', 'nombre_clase3', 'id_clase2')
    list_display_links = ('nombre_clase3',)

@admin.register(EstadoProducto)
class EstadoProductoAdmin(ModelAdmin):
    list_display = ('id_estado', 'nombre_estado')
    list_display_links = ('nombre_estado',)


class ProductoResource(resources.ModelResource):
    id_estado_producto = fields.Field(
        column_name='id_estado_producto',
        attribute='id_estado_producto',
        widget=ForeignKeyWidget(EstadoProducto, 'id_estado')
    )
    id_clase = fields.Field(
        column_name='id_clase',
        attribute='id_clase',
        widget=ForeignKeyWidget(Clase, 'id_clase')
    )

    def before_import_row(self, row, **kwargs):
        # Validar que el nombre no esté vacío
        if not row.get('nombre'):
            raise Exception('El campo nombre es obligatorio.')

    class Meta:
        model = Producto
        fields = (
            'nombre', 'precio_venta', 'coste', 'fecha_de_ingreso', 'existencia',
            'descripcion', 'id_estado_producto', 'id_clase',
            'imagen1', 'imagen2', 'imagen3', 'imagen4', 'is_sale', 'sale_price', 'is_active'
        )
        skip_unchanged = True
        report_skipped = True
        

@admin.register(Producto)
class ProductosAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProductoResource
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=productos.csv'
        writer = csv.writer(response)
        # Escribe el encabezado
        writer.writerow([
            'nombre', 'precio_venta', 'coste', 'fecha_de_ingreso', 'existencia',
            'descripcion', 'id_estado_producto', 'id_clase',
            'imagen1', 'imagen2', 'imagen3', 'imagen4', 'is_sale', 'sale_price', 'is_active'
        ])
        # Escribe los datos
        for producto in queryset:
            writer.writerow([
                producto.nombre, producto.precio_venta, producto.coste, producto.fecha_de_ingreso,
                producto.existencia, producto.descripcion, producto.id_estado_producto_id, producto.id_clase_id,
                producto.imagen1, producto.imagen2, producto.imagen3, producto.imagen4,
                producto.is_sale, producto.sale_price, producto.is_active
            ])
        return response

    export_as_csv.short_description = "Exportar productos seleccionados como CSV"
    import_id_fields = ['nombre']
    import_form_class = ImportForm
    export_form_class = ExportForm
    selectable_fields_export_form_class = SelectableFieldsExportForm
    list_display = ('id_producto', 'nombre', 'precio_venta',
                    'coste', 'fecha_de_ingreso', 'existencia', 'descripcion_corta', 'id_estado_producto', 'id_clase')

    search_fields = ('nombre', 'fecha_de_ingreso',
                     'id_producto', )
    list_per_page = 5
    list_editable = ('id_estado_producto', )

    list_filter = [('fecha_de_ingreso', RangeDateFilter),
                   'id_estado_producto', 'id_clase',]

    list_display_links = ('nombre',)
    ordering = ('id_producto',)
    # Método para truncar la descripción
    def descripcion_corta(self, obj):
        if obj.descripcion:
            return (obj.descripcion[:50] + '...') if len(obj.descripcion) > 50 else obj.descripcion
        return "Sin descripción"

    descripcion_corta.short_description = 'Descripción'
    
