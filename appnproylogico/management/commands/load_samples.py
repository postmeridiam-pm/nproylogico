import json
import pathlib
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.apps import apps


class Command(BaseCommand):
    help = 'Carga datos desde static/data/*.json a la base de datos'

    def handle(self, *args, **options):
        base = pathlib.Path(__file__).resolve().parents[3] / 'static' / 'data'
        now = timezone.now()
        Rol = apps.get_model('appnproylogico', 'Rol')
        Usuario = apps.get_model('appnproylogico', 'Usuario')
        Motorista = apps.get_model('appnproylogico', 'Motorista')
        Moto = apps.get_model('appnproylogico', 'Moto')
        Localfarmacia = apps.get_model('appnproylogico', 'Localfarmacia')
        AsignacionMotoMotorista = apps.get_model('appnproylogico', 'AsignacionMotoMotorista')
        AsignacionMotoristaFarmacia = apps.get_model('appnproylogico', 'AsignacionMotoristaFarmacia')
        Despacho = apps.get_model('appnproylogico', 'Despacho')

        def _get_rol_motorista():
            try:
                r = Rol.objects.filter(codigo='MOTORISTA').first()
                if r:
                    return r
            except Exception:
                pass
            return Rol.objects.first()

        rol_mot = _get_rol_motorista()
        # Generar base para IDs únicos de usuarios stub
        try:
            max_uid = (apps.get_model('appnproylogico','Usuario').objects.order_by('-django_user_id').first().django_user_id or 0)
        except Exception:
            max_uid = 0
        next_uid = max_uid + 1

        # Farmacias
        farm_path = base / 'farmacias.json'
        if farm_path.exists():
            try:
                farms = json.loads(farm_path.read_text(encoding='utf-8'))
                for fa in farms:
                    lid = (str(fa.get('local_id') or '').strip())
                    if not lid:
                        continue
                    apertura_txt = fa.get('funcionamiento_hora_apertura') or '08:00:00'
                    cierre_txt = fa.get('funcionamiento_hora_cierre') or '18:00:00'
                    try:
                        apertura = datetime.time.fromisoformat(apertura_txt)
                    except Exception:
                        apertura = datetime.time(8, 0, 0)
                    try:
                        cierre = datetime.time.fromisoformat(cierre_txt)
                    except Exception:
                        cierre = datetime.time(18, 0, 0)
                    fecha_act_txt = fa.get('fecha_actualizacion') or now.strftime('%Y-%m-%d')
                    try:
                        fecha_act = datetime.date.fromisoformat(fecha_act_txt)
                    except Exception:
                        fecha_act = now.date()
                    Localfarmacia.objects.get_or_create(
                        local_id=lid,
                        defaults={
                            'local_nombre': fa.get('local_nombre') or '',
                            'local_direccion': fa.get('local_direccion') or '',
                            'comuna_nombre': fa.get('comuna_nombre') or '',
                            'localidad_nombre': fa.get('localidad_nombre') or '',
                            'funcionamiento_hora_apertura': apertura,
                            'funcionamiento_hora_cierre': cierre,
                            'funcionamiento_dia': fa.get('funcionamiento_dia') or 'lunes',
                            'local_telefono': fa.get('local_telefono') or '',
                            'local_lat': fa.get('local_lat'),
                            'local_lng': fa.get('local_lng'),
                            'geolocalizacion_validada': False,
                            'fecha_geolocalizacion': None,
                            'fecha': fecha_act,
                            'activo': True,
                            'fecha_creacion': now,
                            'fecha_modificacion': now,
                            'usuario_modificacion': None,
                        }
                    )
            except Exception:
                pass

        # Motoristas
        mot_path = base / 'motoristas.json'
        if mot_path.exists():
            try:
                motoristas = json.loads(mot_path.read_text(encoding='utf-8'))
                for m in motoristas:
                    nombre = (m.get('nombre') or 'Demo').strip()
                    apellido = (m.get('apellido') or 'User').strip()
                    username = f"{nombre}.{apellido}".lower().replace(' ', '.')[:30]
                    doc = (f"MTR-{username}")[:20]
                    user, created_u = Usuario.objects.get_or_create(
                        documento_identidad=doc,
                        defaults={
                            'rol': rol_mot,
                            'tipo_documento': 'RUT',
                            'django_user_id': next_uid,
                            'nombre': nombre,
                            'apellido': apellido,
                            'telefono': '000000000',
                            'activo': True,
                            'fecha_creacion': now,
                            'fecha_modificacion': now,
                        }
                    )
                    if created_u:
                        next_uid += 1
                    Motorista.objects.get_or_create(
                        usuario=user,
                        defaults={
                            'licencia_numero': f"LIC-{username[:8].upper()}",
                            'licencia_clase': 'A',
                            'fecha_vencimiento_licencia': now.date(),
                            'emergencia_nombre': 'Contacto',
                            'emergencia_telefono': '000000000',
                            'emergencia_parentesco': 'Otro',
                            'total_entregas_completadas': 0,
                            'total_entregas_fallidas': 0,
                            'activo': True,
                            'disponible_hoy': True,
                            'fecha_creacion': now,
                            'fecha_modificacion': now,
                        }
                    )
            except Exception:
                pass
        # Completar hasta 200 motoristas
        try:
            total_mot = Motorista.objects.count()
            need = max(200 - total_mot, 0)
            for i in range(need):
                seq = total_mot + i + 1
                nombre = f"Demo"
                apellido = f"Motorista {seq}"
                username = f"demo.{seq}"
                doc = (f"MTR-{seq:06d}")[:20]
                user, created_u = Usuario.objects.get_or_create(
                    documento_identidad=doc,
                    defaults={
                        'rol': rol_mot,
                        'tipo_documento': 'RUT',
                        'django_user_id': next_uid,
                        'nombre': nombre,
                        'apellido': apellido[:80],
                        'telefono': '000000000',
                        'activo': True,
                        'fecha_creacion': now,
                        'fecha_modificacion': now,
                    }
                )
                if created_u:
                    next_uid += 1
                Motorista.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'licencia_numero': f"LIC-{seq:06d}"[:20],
                        'licencia_clase': 'A',
                        'fecha_vencimiento_licencia': now.date(),
                        'emergencia_nombre': 'Contacto',
                        'emergencia_telefono': '000000000',
                        'emergencia_parentesco': 'Otro',
                        'total_entregas_completadas': 0,
                        'total_entregas_fallidas': 0,
                        'activo': True,
                        'disponible_hoy': True,
                        'fecha_creacion': now,
                        'fecha_modificacion': now,
                    }
                )
        except Exception:
            pass

        # Motos
        moto_path = base / 'motos.json'
        if moto_path.exists():
            try:
                motos = json.loads(moto_path.read_text(encoding='utf-8'))
                for mo in motos:
                    patente = (mo.get('patente') or '').strip()
                    if not patente:
                        continue
                    Moto.objects.get_or_create(
                        patente=patente,
                        defaults={
                            'marca': mo.get('marca') or 'GENERICA',
                            'modelo': mo.get('modelo') or 'STD',
                            'anio': int(mo.get('anio') or 2020),
                            'propietario_nombre': 'LOGICO SPA',
                            'propietario_tipo_documento': 'RUT',
                            'propietario_documento': f'RUT-{patente}',
                            'cilindrada_cc': int(mo.get('cilindrada_cc') or 150),
                            'color': (mo.get('color') or 'NEGRO'),
                            'tipo_combustible': 'GASOLINA',
                            'numero_motor': f'MOTOR-{patente}',
                            'numero_chasis': f'CHASIS-{patente}',
                            'fecha_inscripcion': now.date(),
                            'estado': 'EN_USO',
                            'kilometraje_actual': int(mo.get('kilometraje_actual') or 0),
                            'activo': bool(mo.get('activo', True)),
                            'fecha_creacion': now,
                            'fecha_modificacion': now,
                        }
                    )
            except Exception:
                pass
        # Completar hasta 210 motos
        try:
            total_m = Moto.objects.count()
            need = max(210 - total_m, 0)
            for i in range(need):
                idx = total_m + i + 1
                patente = f"PX{idx:04d}"
                Moto.objects.get_or_create(
                    patente=patente,
                    defaults={
                        'marca': 'GENERICA',
                        'modelo': 'STD',
                        'anio': 2020,
                        'propietario_nombre': 'LOGICO SPA',
                        'propietario_tipo_documento': 'RUT',
                        'propietario_documento': f'RUT-{patente}',
                        'cilindrada_cc': 150,
                        'color': 'NEGRO',
                        'tipo_combustible': 'GASOLINA',
                        'numero_motor': f'MOTOR-{patente}',
                        'numero_chasis': f'CHASIS-{patente}',
                        'fecha_inscripcion': now.date(),
                        'estado': 'EN_USO',
                        'kilometraje_actual': 0,
                        'activo': True,
                        'fecha_creacion': now,
                        'fecha_modificacion': now,
                    }
                )
        except Exception:
            pass

        # Asignaciones moto-motorista
        amm_path = base / 'asignaciones_moto_motorista.json'
        if amm_path.exists():
            try:
                asign = json.loads(amm_path.read_text(encoding='utf-8'))
                for a in asign:
                    mot_full = (a.get('motorista') or '').strip()
                    moto_pat = (a.get('moto') or '').strip().upper()
                    if not mot_full or not moto_pat:
                        continue
                    parts = mot_full.split()
                    nombre = parts[0]
                    apellido = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    m = Motorista.objects.filter(usuario__nombre__iexact=nombre, usuario__apellido__icontains=apellido).first()
                    if not m:
                        user, _ = Usuario.objects.get_or_create(
                            django_user_id=0,
                            defaults={
                                'rol': rol_mot,
                                'tipo_documento': 'RUT',
                                'documento_identidad': f"MTR-{nombre}.{apellido}"[:30],
                                'nombre': nombre,
                                'apellido': apellido or 'Demo',
                                'telefono': '000000000',
                                'activo': True,
                                'fecha_creacion': now,
                                'fecha_modificacion': now,
                            }
                        )
                        m = Motorista.objects.get_or_create(
                            usuario=user,
                            defaults={
                                'licencia_numero': f"LIC-{nombre[:8].upper()}",
                                'licencia_clase': 'A',
                                'fecha_vencimiento_licencia': now.date(),
                                'emergencia_nombre': 'Contacto',
                                'emergencia_telefono': '000000000',
                                'emergencia_parentesco': 'Otro',
                                'total_entregas_completadas': 0,
                                'total_entregas_fallidas': 0,
                                'activo': True,
                                'disponible_hoy': True,
                                'fecha_creacion': now,
                                'fecha_modificacion': now,
                            }
                        )[0]
                    mo = Moto.objects.filter(patente=moto_pat).first()
                    if not mo and moto_pat:
                        mo = Moto.objects.create(
                            patente=moto_pat,
                            marca='GENERICA',
                            modelo='STD',
                            estado='ACTIVO',
                            kilometraje_actual=0,
                            activo=True,
                            fecha_creacion=now,
                            fecha_modificacion=now,
                        )
                    AsignacionMotoMotorista.objects.get_or_create(
                        motorista=m,
                        moto=mo,
                        activa=1,
                        defaults={
                            'fecha_asignacion': a.get('fecha_asignacion') or now,
                            'kilometraje_inicio': int(getattr(mo, 'kilometraje_actual', 0) or 0),
                            'observaciones': 'Cargada desde JSON',
                        }
                    )
            except Exception:
                pass

        # Asignaciones motorista-farmacia
        amf_path = base / 'asignaciones_motorista_farmacia.json'
        if amf_path.exists():
            try:
                asign = json.loads(amf_path.read_text(encoding='utf-8'))
                for a in asign:
                    mot_full = (a.get('motorista') or '').strip()
                    farm_val = (a.get('farmacia') or '').strip()
                    if not mot_full or not farm_val:
                        continue
                    parts = mot_full.split()
                    nombre = parts[0]
                    apellido = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    m = Motorista.objects.filter(usuario__nombre__iexact=nombre, usuario__apellido__icontains=apellido).first()
                    f = Localfarmacia.objects.filter(local_id=farm_val).first()
                    if not f:
                        f = Localfarmacia.objects.filter(local_nombre__icontains=farm_val).first()
                    if not (m and f):
                        continue
                    AsignacionMotoristaFarmacia.objects.get_or_create(
                        motorista=m,
                        farmacia=f,
                        activa=1,
                        defaults={
                            'fecha_asignacion': a.get('fecha_asignacion') or now,
                            'observaciones': 'Cargada desde JSON',
                        }
                    )
            except Exception:
                pass

        # Despachos demo
        try:
            import random
            tipos = ['DOMICILIO', 'INTERCAMBIO', 'REENVIO_RECETA']
            prios = ['ALTA', 'MEDIA', 'BAJA']
            oper = Usuario.objects.first()
            farms = list(Localfarmacia.objects.all()[:10])
            motos = list(Moto.objects.all()[:10])
            motores = list(Motorista.objects.all()[:20])
            count = 0
            for i in range(20):
                if not motores:
                    break
                mot = motores[i % len(motores)]
                farm = farms[i % len(farms)] if farms else None
                codigo = f"DSP-{now.strftime('%Y%m%d')}-{i:04d}"
                if Despacho.objects.filter(codigo_despacho=codigo).exists():
                    continue
                tipo = tipos[i % len(tipos)]
                pr = prios[i % len(prios)]
                tiene_receta = (tipo == 'REENVIO_RECETA')
                d = Despacho(
                    codigo_despacho=codigo,
                    numero_orden_farmacia=f"ORD-{i:04d}",
                    farmacia_origen_local_id=(farm.local_id if farm else '7001'),
                    motorista=mot,
                    estado='PENDIENTE',
                    tipo_despacho=tipo,
                    prioridad=pr,
                    cliente_nombre=f"Cliente {i}",
                    cliente_telefono='+56900000000',
                    destino_direccion=f"Calle {i} #123, Comuna",
                    destino_referencia='Puerta negra',
                    destino_lat=None,
                    destino_lng=None,
                    destino_geolocalizacion_validada=False,
                    tiene_receta_retenida=tiene_receta,
                    numero_receta=(f"REC-{i:05d}" if tiene_receta else None),
                    requiere_devolucion_receta=tiene_receta,
                    receta_devuelta_farmacia=False,
                    descripcion_productos='Caja de medicamentos',
                    valor_declarado=0,
                    requiere_aprobacion_operadora=False,
                    aprobado_por_operadora=False,
                    usuario_aprobador=None,
                    fecha_aprobacion=None,
                    usuario_registro=oper,
                    usuario_modificacion=None,
                    fecha_registro=now,
                    fecha_asignacion=None,
                    fecha_modificacion=now,
                    hubo_incidencia=False,
                    tipo_incidencia=None,
                )
                try:
                    d.save(); count += 1
                except Exception:
                    pass
        except Exception:
            pass

        # Asegurar asignaciones moto–motorista visibles
        try:
            motores = list(Motorista.objects.all().order_by('id')[:200])
            motos_all = list(Moto.objects.all().order_by('patente')[:210])
            paired = min(len(motores), len(motos_all), 200)
            for i in range(paired):
                m = motores[i]
                mo = motos_all[i]
                AsignacionMotoMotorista.objects.get_or_create(
                    motorista=m,
                    moto=mo,
                    activa=1,
                    defaults={
                        'fecha_asignacion': now,
                        'kilometraje_inicio': int(getattr(mo, 'kilometraje_actual', 0) or 0),
                        'observaciones': 'Asignación de demostración automática',
                    }
                )
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS('Datos de JSON cargados (motoristas, motos, asignaciones)'))
