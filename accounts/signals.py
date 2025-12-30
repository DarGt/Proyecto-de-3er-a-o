from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Usuario

# Cuando se registre un usuario, se ejecutará la operación para asignarlo a un grupo.

@receiver(post_save, sender=Usuario)
def agregar_usuario_a_grupo(sender, instance, created, **kwargs):
    if created:
        try:
            grupo1 = Group.objects.get(name="usuarios")
        except Group.DoesNotExist:
            grupo1 = Group.objects.create(name="usuarios")
            grupo2 =Group.objects.create(name="caja")
            grupo3 =Group.objects.create(name="almacen")
            grupo4 =Group.objects.create(name="administrativos")
        instance.user.groups.add(grupo1)
        
# Crear y guardar el perfil del usuario cuando se crea un nuevo User.


