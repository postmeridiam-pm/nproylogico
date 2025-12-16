from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from appnproylogico.models import Despacho, Localfarmacia


def _fallback_ai(despacho, horario_cierre="20:00"):
    estado = (getattr(despacho, 'estado', '') or 'Desconocido').upper()
    prioridad = getattr(despacho, 'prioridad', '') or 'No definida'
    cliente = getattr(despacho, 'cliente_nombre', '') or 'Cliente'
    lid = (getattr(despacho, 'farmacia_origen_local_id', '') or '').strip()
    now_t = timezone.now().time()
    cierre_t = None
    try:
        farm = Localfarmacia.objects.filter(local_id=lid).first()
        cierre_t = getattr(farm, 'funcionamiento_hora_cierre', None)
    except Exception:
        cierre_t = None
    dt_now = timezone.now()
    minutos_restantes = None
    try:
        if cierre_t:
            cierre_dt = dt_now.replace(hour=cierre_t.hour, minute=cierre_t.minute, second=0, microsecond=0)
            minutos_restantes = max(0, int((cierre_dt - dt_now).total_seconds() // 60))
    except Exception:
        minutos_restantes = None
    minutos_en_ruta = None
    try:
        fs = getattr(despacho, 'fecha_salida_farmacia', None)
        if fs:
            minutos_en_ruta = max(0, int((dt_now - fs).total_seconds() // 60))
    except Exception:
        minutos_en_ruta = None
    acciones = []
    sugerencia = 'Postergar'
    pr = prioridad.upper()
    if estado == 'FALLIDO':
        sugerencia = 'Reasignar/Reenviar'
        acciones = ['Asignar motorista cercano', 'Avisar a cliente y farmacia']
    elif pr == 'ALTA':
        sugerencia = 'Confirmar entrega/Acciones'
        acciones = ['Llamar cliente para recepción', 'Optimizar ruta']
    elif estado in {'EN_CAMINO','EN_PROCESO'}:
        sugerencia = 'Confirmar entrega/Acciones'
        acciones = ['Mantener curso', 'Confirmar llegada con cliente']
    if minutos_restantes is not None:
        if minutos_restantes == 0 and pr != 'ALTA':
            sugerencia = 'Postergar'
            acciones = ['Reprogramar al día siguiente']
        elif pr == 'ALTA' and minutos_restantes < 30:
            sugerencia = 'Confirmar entrega/Acciones'
            acciones = ['Asignar apoyo inmediato', 'Priorizar llegada']
    resumen = f"{estado} · {prioridad} · {cliente}"
    detalle = (f" · Ruta {minutos_en_ruta} min" if minutos_en_ruta is not None else '') + (f" · Restan {minutos_restantes} min" if minutos_restantes is not None else '')
    acciones_txt = ('; '.join(acciones) if acciones else 'Sin acciones adicionales')
    return f"Resumen: {resumen}{detalle}\nSugerencia: {sugerencia} ({acciones_txt})"


class Command(BaseCommand):
    help = "Ejecuta un análisis IA sobre el último despacho"

    def add_arguments(self, parser):
        parser.add_argument('--examples', action='store_true', help='Muestra ejemplos de sugerencias por estado/prioridad')
        parser.add_argument('--estado', type=str, default=None, help='Filtra por estado (ej: FALLIDO)')
        parser.add_argument('--limit', type=int, default=200, help='Máximo de registros a analizar')

    def handle(self, *args, **options):
        ai = _fallback_ai
        if options.get('examples'):
            estados = ['FALLIDO','EN_CAMINO','EN_PROCESO','PENDIENTE']
            prioridades = ['ALTA','MEDIA','BAJA']
            class D:
                def __init__(self, estado, prioridad):
                    self.estado = estado
                    self.prioridad = prioridad
                    self.cliente_nombre = 'Cliente Uno'
                    self.farmacia_origen_local_id = 'CV-0001'
            horario = getattr(settings, 'HORARIO_CIERRE_DEFAULT', '20:00')
            for e in estados:
                for p in prioridades:
                    out = ai(D(e,p), horario_cierre=horario)
                    self.stdout.write(f"{e} · {p} → {out.split('\n')[-1]}")
            return
        estado = (options.get('estado') or '').strip().upper()
        limit = int(options.get('limit') or 200)
        if estado:
            qs = Despacho.objects.all().order_by('-fecha_registro')
            qs = qs.filter(estado=estado)
            horario = getattr(settings, 'HORARIO_CIERRE_DEFAULT', '20:00')
            count = 0
            for d in qs[:limit]:
                out = ai(d, horario_cierre=horario)
                codigo = d.codigo_despacho or d.id
                self.stdout.write(f"{codigo} · {d.estado} · {d.prioridad} → {out.split('\n')[-1]}")
                count += 1
            if count == 0:
                self.stdout.write(self.style.WARNING("Sin registros para el estado indicado"))
            return
        d = Despacho.objects.order_by('-fecha_registro').first()
        if not d:
            self.stdout.write(self.style.ERROR("No hay despachos para analizar"))
            return
        horario = getattr(settings, 'HORARIO_CIERRE_DEFAULT', '20:00')
        res = ai(d, horario_cierre=horario)
        self.stdout.write(str(res))
