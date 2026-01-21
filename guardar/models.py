from django.db import models
from accounts.models import Usuario
from django.contrib.auth.models import User
# Create your models here.
import time
from django.core.exceptions import ValidationError


class SugerenciaEliminacion(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()
    aceptada = models.BooleanField(default=False)  # Nuevo campo

    def __str__(self):
        return f"Sugerencia de eliminación para {self.producto.nombre} por {self.usuario.username}"
    
    def aceptar(self):
        # Elimina el producto y marca la sugerencia como aceptada
        self.producto.is_active = False
        self.aceptada = True
        self.save(update_fields=['aceptada'])
        self.producto.delete()

class EstadoProducto(models.Model):
    id_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_estado


class Clase(models.Model):
    id_clase = models.AutoField(primary_key=True)
    nombre_clase = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_clase

class Clase2(models.Model):
    id_clase2 = models.AutoField(primary_key=True)
    nombre_clase2 = models.CharField(max_length=50)
    id_clase = models.ForeignKey(Clase, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_clase2

class Clase3(models.Model):
    id_clase3 = models.AutoField(primary_key=True)
    nombre_clase3 = models.CharField(max_length=50)
    id_clase2 = models.ForeignKey(Clase2, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_clase3


class SubClase(models.Model):
    id_sub_clase = models.AutoField(primary_key=True)
    nombre_sub_clase = models.CharField(max_length=50)
    id_clase = models.ForeignKey(Clase, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_sub_clase


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    coste = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_de_ingreso = models.DateField()
    existencia = models.IntegerField()
    descripcion = models.TextField(null=True, blank=True, verbose_name='Descripcion')
    id_estado_producto = models.ForeignKey(
        EstadoProducto, on_delete=models.SET_NULL, null=True)
    id_clase = models.ForeignKey(Clase, on_delete=models.SET_NULL, null=True)
    id_clase2 = models.ForeignKey(Clase2, on_delete=models.SET_NULL, null=True)
    id_clase3 = models.ForeignKey(Clase3, on_delete=models.SET_NULL, null=True, blank=True, )
    imagen1 = models.ImageField(default="users/usuario.png", upload_to='imagenes/', null=True, blank=False, verbose_name='Imagen 1')
    imagen2 = models.ImageField(default="users/usuario.png",upload_to='imagenes/', null=True, blank=True, verbose_name='Imagen 2')
    imagen3 = models.ImageField(default="users/usuario.png",upload_to='imagenes/', null=True, blank=True, verbose_name='Imagen 3')
    imagen4 = models.ImageField(default="users/usuario.png",upload_to='imagenes/', null=True, blank=True, verbose_name='Imagen 4')
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6, verbose_name="precio de oferta")
    like = models.ManyToManyField(User,related_name="posts", verbose_name="Me gusta ")
    is_active = models.BooleanField(default=True)
    def __str__(self):
        fila = "Nombre: " + self.nombre + " - " + "Clase: " + \
            self.id_clase.nombre_clase + " - " + "Descripción: " + str(self.descripcion)
        return fila

    def clean(self):
        
        if not self.imagen1 and not self.imagen2 and not self.imagen3 and not self.imagen4:
            raise ValidationError('Debes subir al menos una imagen para el producto.')

    def delete(self, using=None, keep_parents=False):
       
        for img in [self.imagen1, self.imagen2, self.imagen3, self.imagen4]:
            if img:
                img.storage.delete(img.name)
        super().delete(using=using, keep_parents=keep_parents)
    _ultimo_guardado = 0 
    
    def save(self, *args, **kwargs):
        tiempo_actual = time.time()
        if tiempo_actual - Producto._ultimo_guardado < 2:
            raise ValidationError("Debes esperar 2 segundos antes de agregar otro producto.")
        super().save(*args, **kwargs)
        Producto._ultimo_guardado = tiempo_actual

class Perdida(models.Model):
    id_perdida = models.AutoField(primary_key=True)
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    id_estado = models.ForeignKey(
        EstadoProducto, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"Perdida #{self.id_perdida} - {self.fecha} - Total: ${self.total}"

class CantidadPerdida(models.Model):
    id_c_perdida = models.AutoField(primary_key=True)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    id_producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True)
    id_perdida = models.ForeignKey(Perdida, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.id_producto:
            # Solo descuenta si es una creación, no edición
            if not self.pk:
                self.id_producto.existencia -= self.cantidad
                self.id_producto.save()
        super().save(*args, **kwargs)
    def __str__(self):
        producto_nombre = self.id_producto.nombre if self.id_producto else "Sin producto"
        return f"{producto_nombre} - {self.cantidad} unidades - Perdida #{self.id_perdida.id_perdida}"


class DetalleProveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    correo = models.CharField(max_length=100)


class DetallesCambio(models.Model):
    id_cambio = models.AutoField(primary_key=True)
    fecha_cambio = models.DateField()
    tipo_cambio = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    id_producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True)


# --- AGREGAR AL FINAL DE models.py ---

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Tu modelo de usuario
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Venta #{self.id_venta} - {self.fecha.strftime('%d/%m/%Y')}"

class DetalleVenta(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Guardamos el precio del momento de la compra
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en Venta #{self.venta.id_venta}"