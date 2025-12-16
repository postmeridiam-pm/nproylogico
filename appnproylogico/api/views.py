from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, BasePermission
from ..models import Localfarmacia, Motorista, Moto
from .serializers import LocalfarmaciaSerializer, MotoristaSerializer, MotoSerializer
from ..roles import obtener_permisos_usuario

class HasModuleViewPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            perms = obtener_permisos_usuario(request.user)
            mod = getattr(view, 'module_name', None)
            if not mod:
                return True
            actions = perms.get(mod) or set()
            return ('view' in actions) or ('all' in actions)
        except Exception:
            return False

class FarmaciaList(generics.ListAPIView):
    queryset = Localfarmacia.objects.all().order_by('local_nombre')
    serializer_class = LocalfarmaciaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['local_nombre','local_direccion','comuna_nombre']
    permission_classes = [IsAuthenticated, HasModuleViewPermission]
    module_name = 'farmacias'

class MotoristaList(generics.ListAPIView):
    queryset = Motorista.objects.select_related('usuario').all().order_by('usuario__nombre')
    serializer_class = MotoristaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['usuario__nombre','usuario__apellido','licencia_numero']
    permission_classes = [IsAuthenticated, HasModuleViewPermission]
    module_name = 'motoristas'

class MotoList(generics.ListAPIView):
    queryset = Moto.objects.all().order_by('patente')
    serializer_class = MotoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['patente','marca','modelo']
    permission_classes = [IsAuthenticated, HasModuleViewPermission]
    module_name = 'motos'
