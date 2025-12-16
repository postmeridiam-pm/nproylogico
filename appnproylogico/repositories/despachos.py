from django.db.models import F, Value, CharField, OuterRef, Subquery, IntegerField
from django.db.models.functions import Concat, Cast
from appnproylogico.models import Despacho, Localfarmacia, Motorista, AsignacionMotoMotorista, NormalizacionDespacho

def get_despachos_activos():
    estados = ['PENDIENTE', 'ASIGNADO', 'PREPARANDO', 'PREPARADO', 'EN_CAMINO']
    farmacia_nombre = Subquery(
        Localfarmacia.objects.filter(local_id=OuterRef('farmacia_origen_local_id')).values('local_nombre')[:1]
    )
    moto_patente = Subquery(
        AsignacionMotoMotorista.objects.filter(motorista=OuterRef('motorista'), activa=True).values('moto__patente')[:1]
    )
    coords = Concat(Cast('destino_lat', CharField()), Value(','), Cast('destino_lng', CharField()))
    return Despacho.objects.filter(estado__in=estados).annotate(
        farmacia_origen=farmacia_nombre,
        motorista_nombre=Concat(F('motorista__usuario__nombre'), Value(' '), F('motorista__usuario__apellido'), output_field=CharField()),
        moto_patente=moto_patente,
        coordenadas_destino=coords,
        minutos_en_ruta=Value(None, output_field=IntegerField()),
    ).values_list(
        'id',
        'codigo_despacho',
        'estado',
        'tipo_despacho',
        'prioridad',
        'farmacia_origen',
        'motorista_nombre',
        'moto_patente',
        'cliente_nombre',
        'cliente_telefono',
        'destino_direccion',
        'tiene_receta_retenida',
        'requiere_aprobacion_operadora',
        'aprobado_por_operadora',
        'fecha_registro',
        'fecha_asignacion',
        'fecha_salida_farmacia',
        'minutos_en_ruta',
        'hubo_incidencia',
        'tipo_incidencia',
        'coordenadas_destino',
    )

def get_resumen_operativo_hoy():
    return []

def get_resumen_operativo_mes(anio=None, mes=None):
    return []

def get_resumen_operativo_anual(anio=None):
    return []

def normalize_from_normalizacion(limit=100):
    qs = NormalizacionDespacho.objects.filter(procesado=False).order_by('id')[:limit]
    for n in qs:
        n.procesado = True
        n.error_normalizacion = None
        n.save(update_fields=['procesado','error_normalizacion'])
