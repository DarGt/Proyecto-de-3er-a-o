from django.db import models
from accounts.models import Usuario
from guardar.models import  Producto
import datetime

#pedidos de clientes orden

class Order(models.Model):
    id_producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    direccion = models.CharField(max_length=100, default=" ", blank=True)
    telefono = models.CharField(max_length=20, default=" ", blank=True)
    fecha = models.DateTimeField(default=datetime.datetime.today)
    estatus = models.BooleanField(default=False)


    def __str__(self):
        return str(self.id_producto)


# Modelo para comentarios de productos
class Comentario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto = models.TextField()
    calificacion = models.IntegerField(default=5)
    fecha = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.usuario} - {self.producto} ({self.calificacion})"


# Modelo para likes de productos
class Like(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE,related_name='likes')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('producto', 'usuario')

    def __str__(self):
        return f"Like: {self.usuario} -> {self.producto}"
