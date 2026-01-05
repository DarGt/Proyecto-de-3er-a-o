from rest_framework import serializers
from .models import Usuario


class usuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__' # Trae todos los campos