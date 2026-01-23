from rest_framework import serializers
from .models import Producto, Venta, DetalleVenta


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__' # Trae todos los campos
        
# serializers.py

# 1. Serializador para los detalles (los productos dentro de la venta)
class DetalleVentaSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source='producto.nombre', read_only=True) # Truco Senior: Traemos el nombre directo

    class Meta:
        model = DetalleVenta
        fields = ['id_detalle', 'producto', 'nombre_producto', 'cantidad', 'precio_unitario', 'subtotal']

# 2. Serializador para la Cabecera de la Venta
class VentaSerializer(serializers.ModelSerializer):
    # AQUÍ ESTÁ LA MAGIA: Incrustamos los detalles dentro de la venta
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    
    fecha_formateada = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = ['id_venta', 'fecha', 'fecha_formateada', 'total', 'detalles']

    def get_fecha_formateada(self, obj):
        return obj.fecha.strftime('%d/%m/%Y %H:%M')