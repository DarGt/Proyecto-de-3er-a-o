from django.contrib import admin
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

from .models import Usuario, Domicilio, EstadoCuentaUsuario


# Register your models here. puedo pasar mis modelos al panel de admind de dj
#perfil con datos completos


class PerfilAdmin(ModelAdmin):
    list_display = ("user", "address", "location", "telephone", "user_grup")
    search_fields = ("location", "user_username", "user_groups_name")
    list_filter = ("user__groups", "location")
    
    def user_grup(self, obj):
        return " - ".join([t.name for t in obj.user.groups.all().order_by("name")])
    user_grup.short_description = "Grupo"
admin.site.register(Usuario, PerfilAdmin)

class DomicilioAdmin(ModelAdmin):
    list_display = ("id_domicilio", "sexo", "id_usuario")
    search_fields = ("id_usuario__user__username", "sexo")
    list_filter = ("sexo",)

admin.site.register(Domicilio, DomicilioAdmin)

@admin.register(EstadoCuentaUsuario)
class EstadoCuentaUsuarioAdmin(ModelAdmin):
    list_display = ('user', 'solicitar_eliminacion', 'fecha_solicitud', 'puede_eliminarse')
    list_filter = ('solicitar_eliminacion',)
    search_fields = ('user__username',)

    def puede_eliminarse(self, obj):
        """Muestra si la cuenta ya puede eliminarse en el panel de administración."""
        return obj.puede_eliminarse
    puede_eliminarse.boolean = True
    puede_eliminarse.short_description = "Puede eliminarse"