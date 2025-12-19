from django.db.models import F, Value, CharField, OuterRef, Subquery, IntegerField, Sum, Count, Case, When, Q, Max
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
    from django.utils import timezone
    hoy = timezone.now().date()
    farmacia_nombre = Subquery(Localfarmacia.objects.filter(local_id=OuterRef('farmacia_origen_local_id')).values('local_nombre')[:1])
    comuna_nombre = Subquery(Localfarmacia.objects.filter(local_id=OuterRef('farmacia_origen_local_id')).values('comuna_nombre')[:1])
    qs = Despacho.objects.filter(fecha_registro__date=hoy)
    if not qs.exists():
        try:
            latest = Despacho.objects.aggregate(mx=Max('fecha_registro')).get('mx')
            if latest:
                qs = Despacho.objects.filter(fecha_registro__date=latest.date())
        except Exception:
            pass
    agg = qs.values('farmacia_origen_local_id').annotate(
        farmacia=farmacia_nombre,
        comuna=comuna_nombre,
        total=Count('id'),
        ok=Sum(Case(When(estado='ENTREGADO', then=1), default=0, output_field=IntegerField())),
        fallidos=Sum(Case(When(estado='FALLIDO', then=1), default=0, output_field=IntegerField())),
        en_camino=Sum(Case(When(estado='EN_CAMINO', then=1), default=0, output_field=IntegerField())),
        pendientes=Sum(Case(When(estado__in=['PENDIENTE','ASIGNADO','PREPARANDO','PREPARADO'], then=1), default=0, output_field=IntegerField())),
        anulados=Sum(Case(When(estado='ANULADO', then=1), default=0, output_field=IntegerField())),
        con_receta=Sum(Case(When(tiene_receta_retenida=True, then=1), default=0, output_field=IntegerField())),
        con_incidencias=Sum(Case(When(hubo_incidencia=True, then=1), default=0, output_field=IntegerField())),
        tiempo_promedio=Value(0, output_field=IntegerField()),
        valor_total=Sum(Case(When(valor_declarado__isnull=False, then=F('valor_declarado')), default=0, output_field=IntegerField())),
        directo=Sum(Case(When(tipo_despacho='DOMICILIO', then=1), default=0, output_field=IntegerField())),
        reenvio_receta=Sum(Case(When(tipo_despacho='REENVIO_RECETA', then=1), default=0, output_field=IntegerField())),
        intercambio=Sum(Case(When(tipo_despacho__in=['INTERCAMBIO','INTERCAMBIO_FARMACIAS'], then=1), default=0, output_field=IntegerField())),
        error_despacho=Sum(Case(When(tipo_despacho='ERROR_DESPACHO', then=1), default=0, output_field=IntegerField())),
    ).order_by('farmacia_origen_local_id')
    rows = []
    for a in agg:
        rows.append([
            a.get('farmacia_origen_local_id'),
            a.get('farmacia') or '',
            a.get('comuna') or '',
            a.get('total') or 0,
            a.get('ok') or 0,
            a.get('fallidos') or 0,
            a.get('en_camino') or 0,
            a.get('pendientes') or 0,
            a.get('anulados') or 0,
            a.get('con_receta') or 0,
            a.get('con_incidencias') or 0,
            a.get('tiempo_promedio') or 0,
            a.get('valor_total') or 0,
            a.get('directo') or 0,
            a.get('reenvio_receta') or 0,
            a.get('intercambio') or 0,
            a.get('error_despacho') or 0,
        ])
    return rows

def get_resumen_operativo_mes(anio=None, mes=None):
    from django.utils import timezone
    hoy = timezone.now().date()
    y = int(anio) if anio else hoy.year
    m = int(mes) if mes else hoy.month
    farmacia_nombre = Subquery(Localfarmacia.objects.filter(local_id=OuterRef('farmacia_origen_local_id')).values('local_nombre')[:1])
    comuna_nombre = Subquery(Localfarmacia.objects.filter(local_id=OuterRef('farmacia_origen_local_id')).values('comuna_nombre')[:1])
    qs = Despacho.objects.filter(fecha_registro__year=y, fecha_registro__month=m)
    agg = qs.values('farmacia_origen_local_id').annotate(
        farmacia=farmacia_nombre,
        comuna=comuna_nombre,
        total=Count('id'),
        ok=Sum(Case(When(estado='ENTREGADO', then=1), default=0, output_field=IntegerField())),
        fallidos=Sum(Case(When(estado='FALLIDO', then=1), default=0, output_field=IntegerField())),
        en_camino=Sum(Case(When(estado='EN_CAMINO', then=1), default=0, output_field=IntegerField())),
        pendientes=Sum(Case(When(estado__in=['PENDIENTE','ASIGNADO','PREPARANDO','PREPARADO'], then=1), default=0, output_field=IntegerField())),
        anulados=Sum(Case(When(estado='ANULADO', then=1), default=0, output_field=IntegerField())),
        con_receta=Sum(Case(When(tiene_receta_retenida=True, then=1), default=0, output_field=IntegerField())),
        con_incidencias=Sum(Case(When(hubo_incidencia=True, then=1), default=0, output_field=IntegerField())),
        tiempo_promedio=Value(0, output_field=IntegerField()),
        valor_total=Sum(Case(When(valor_declarado__isnull=False, then=F('valor_declarado')), default=0, output_field=IntegerField())),
        directo=Sum(Case(When(tipo_despacho='DOMICILIO', then=1), default=0, output_field=IntegerField())),
        reenvio_receta=Sum(Case(When(tipo_despacho='REENVIO_RECETA', then=1), default=0, output_field=IntegerField())),
        intercambio=Sum(Case(When(tipo_despacho__in=['INTERCAMBIO','INTERCAMBIO_FARMACIAS'], then=1), default=0, output_field=IntegerField())),
        error_despacho=Sum(Case(When(tipo_despacho='ERROR_DESPACHO', then=1), default=0, output_field=IntegerField())),
    ).order_by('farmacia_origen_local_id')
    rows = []
    for a in agg:
        rows.append([
            y,
            m,
            a.get('farmacia_origen_local_id'),
            a.get('farmacia') or '',
            a.get('comuna') or '',
            a.get('total') or 0,
            a.get('ok') or 0,
            a.get('fallidos') or 0,
            a.get('en_camino') or 0,
            a.get('pendientes') or 0,
            a.get('anulados') or 0,
            a.get('con_receta') or 0,
            a.get('con_incidencias') or 0,
            a.get('tiempo_promedio') or 0,
            a.get('valor_total') or 0,
            a.get('directo') or 0,
            a.get('reenvio_receta') or 0,
            a.get('intercambio') or 0,
            a.get('error_despacho') or 0,
        ])
    return rows

def get_resumen_operativo_anual(anio=None):
    from django.utils import timezone
    hoy = timezone.now().date()
    y = int(anio) if anio else hoy.year
    farmacia_nombre = Subquery(Localfarmacia.objects.filter(local_id=OuterRef('farmacia_origen_local_id')).values('local_nombre')[:1])
    comuna_nombre = Subquery(Localfarmacia.objects.filter(local_id=OuterRef('farmacia_origen_local_id')).values('comuna_nombre')[:1])
    qs = Despacho.objects.filter(fecha_registro__year=y)
    agg = qs.values('farmacia_origen_local_id').annotate(
        farmacia=farmacia_nombre,
        comuna=comuna_nombre,
        total=Count('id'),
        ok=Sum(Case(When(estado='ENTREGADO', then=1), default=0, output_field=IntegerField())),
        fallidos=Sum(Case(When(estado='FALLIDO', then=1), default=0, output_field=IntegerField())),
        en_camino=Sum(Case(When(estado='EN_CAMINO', then=1), default=0, output_field=IntegerField())),
        pendientes=Sum(Case(When(estado__in=['PENDIENTE','ASIGNADO','PREPARANDO','PREPARADO'], then=1), default=0, output_field=IntegerField())),
        anulados=Sum(Case(When(estado='ANULADO', then=1), default=0, output_field=IntegerField())),
        con_receta=Sum(Case(When(tiene_receta_retenida=True, then=1), default=0, output_field=IntegerField())),
        con_incidencias=Sum(Case(When(hubo_incidencia=True, then=1), default=0, output_field=IntegerField())),
        tiempo_promedio=Value(0, output_field=IntegerField()),
        valor_total=Sum(Case(When(valor_declarado__isnull=False, then=F('valor_declarado')), default=0, output_field=IntegerField())),
        directo=Sum(Case(When(tipo_despacho='DOMICILIO', then=1), default=0, output_field=IntegerField())),
        reenvio_receta=Sum(Case(When(tipo_despacho='REENVIO_RECETA', then=1), default=0, output_field=IntegerField())),
        intercambio=Sum(Case(When(tipo_despacho__in=['INTERCAMBIO','INTERCAMBIO_FARMACIAS'], then=1), default=0, output_field=IntegerField())),
        error_despacho=Sum(Case(When(tipo_despacho='ERROR_DESPACHO', then=1), default=0, output_field=IntegerField())),
    ).order_by('farmacia_origen_local_id')
    rows = []
    for a in agg:
        rows.append([
            y,
            a.get('farmacia_origen_local_id'),
            a.get('farmacia') or '',
            a.get('comuna') or '',
            a.get('total') or 0,
            a.get('ok') or 0,
            a.get('fallidos') or 0,
            a.get('en_camino') or 0,
            a.get('pendientes') or 0,
            a.get('anulados') or 0,
            a.get('con_receta') or 0,
            a.get('con_incidencias') or 0,
            a.get('tiempo_promedio') or 0,
            a.get('valor_total') or 0,
            a.get('directo') or 0,
            a.get('reenvio_receta') or 0,
            a.get('intercambio') or 0,
            a.get('error_despacho') or 0,
        ])
    return rows

def normalize_from_normalizacion(limit=100):
    qs = NormalizacionDespacho.objects.filter(procesado=False).order_by('id')[:limit]
    for n in qs:
        n.procesado = True
        n.error_normalizacion = None
        n.save(update_fields=['procesado','error_normalizacion'])
