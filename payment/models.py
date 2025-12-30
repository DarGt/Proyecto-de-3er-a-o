from django.db import models
from django.contrib.auth.models import User
# from core.models import Usuario
from guardar.models import Producto
from django.dispatch import receiver
import datetime
from django.db.models.signals import post_save, pre_save
from django.utils.timezone import now


class ShippingAddress(models.Model):#direccion de envio
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	shipping_full_name = models.CharField(max_length=255)
	shipping_email = models.CharField(max_length=255)
	shipping_address1 = models.CharField(max_length=255)
	shipping_city = models.CharField(max_length=255)
	shipping_state = models.CharField(max_length=255, null=True, blank=True)
	shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
	shipping_country = models.CharField(max_length=255)

	class Meta:
		verbose_name_plural = "Shipping Address"#direccion de envio

	def __str__(self):
		return f'Direccion Completa - {str(self.id)}'

#crear modelo de pedidos y ordenes d eproducto
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    full_name = models.CharField(max_length=250, verbose_name="Nombre Completo")
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=15000, verbose_name="Dirección Completa")

    amount_paid = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Cantidad a pagar")
    date_ordered = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de orden")
    method = models.CharField(max_length=50, verbose_name="Método de pago", default="Stripe")  # Ejemplo: "Stripe", "PayPal"

    shipped = models.BooleanField(default=False, verbose_name="¿Enviado?")
    date_shipped = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de envío")
    recibido = models.BooleanField(default=False, verbose_name="¿Recibido?")

    def save(self, *args, **kwargs):
        if self.shipped and not self.date_shipped:  # Si se marca como enviado y no tiene fecha de envío
            self.date_shipped = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Orden - {str(self.id)}'

@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
	if instance.pk:
		now = datetime.datetime.now()
		obj = sender._default_manager.get(pk=instance.pk)
		if instance.shipped and not obj.shipped:
			instance.date_shipped = now

class OrderItem(models.Model):
    # Foreign Keys
	order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True ,related_name="items")
	product = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True,verbose_name="Producto")#!!cambiar
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	quantity = models.PositiveBigIntegerField(default=1,verbose_name="Cantidad" )
	price = models.DecimalField(max_digits=7, decimal_places=2,verbose_name="Precio")



	def __str__(self):
		return f'items de orden - {str(self.id)}'

