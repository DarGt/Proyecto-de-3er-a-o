from django.db import models
from django.contrib.auth.models import User#import
from django.db.models.signals import post_save #esto me permite crear un perfil para mi usuario
from datetime import timedelta, date

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Usuario")
    date_modifile = models.DateField(User, auto_now=True)
    image = models.ImageField(default="users/usuario.png", upload_to="users/", verbose_name="imagen de perfil")
    address = models.CharField(max_length=150, null=True,blank=True, verbose_name="Direccion")
    #address_2 = models.CharField(max_length=150, null=True,blank=True, verbose_name="Direccion_2")
    location = models.CharField(max_length=150, null=True,blank=True, verbose_name="Localidad")
    city = models.CharField(max_length=150, null=True,blank=True, verbose_name="ciudad")
    state = models.CharField(max_length=150, null=True,blank=True, verbose_name="estado")
    zipcode = models.CharField(max_length=150, null=True,blank=True, verbose_name="codigo  postal")
    telephone = models.CharField(max_length=40, null=True,blank=True, verbose_name="Telefono")
    country =models.CharField(max_length=150, null=True,blank=True, verbose_name="pais")
    created_by_admin = models.BooleanField(default=True, blank=True, null=True,verbose_name="Creado por Admin")
    #este se usar para la percistencia del carrito es decir que no se pierdan los datos del usuario en el cart
    #basicamente el guardar un carrio es complicado asi que es mejor guardarlo mo str en ves de por opartes luego lo #combertiremos en una diccionario 
    old_cart = models.CharField(max_length=250,null=True,blank=True, verbose_name="carrito antiguo")
    
    class Meta:
        verbose_name= "perfil"
        verbose_name_plural= "perfiles"
        ordering = ["-id_usuario"]
        
    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Usuario.objects.create(user = instance)
        
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
    #id_nivel_de_usuario = models.ForeignKey(NivelDeUsuario, on_delete=models.SET_NULL, null=True)
#!!!

class Domicilio(models.Model):
    id_domicilio = models.AutoField(primary_key=True)
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)




class EstadoCuentaUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="estado_cuenta", verbose_name="Usuario")
    solicitar_eliminacion = models.BooleanField(default=False, verbose_name="Solicitar Eliminación")
    motivo_borrado = models.TextField(null=True, blank=True, verbose_name="Motivo de Borrado")
    fecha_solicitud = models.DateField(null=True, blank=True, verbose_name="Fecha de Solicitud")

    def save(self, *args, **kwargs):
        if self.solicitar_eliminacion and not self.fecha_solicitud:
            self.fecha_solicitud = date.today()
        super().save(*args, **kwargs)
        
    @property
    def puede_eliminarse(self):
        """Determina si han pasado los 15 días desde la solicitud."""
        if self.fecha_solicitud:
            return date.today() >= (self.fecha_solicitud + timedelta(days=15))
        return False

    def __str__(self):
        return f"Estado de cuenta de {self.user.username} - Eliminación solicitada: {self.solicitar_eliminacion}"