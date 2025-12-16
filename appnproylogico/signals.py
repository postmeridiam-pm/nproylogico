from django.db.models.signals import pre_save
from django.dispatch import receiver
import hashlib, json
from .models import AuditoriaGeneral

@receiver(pre_save, sender=AuditoriaGeneral)
def _auditoria_hash(sender, instance, **kwargs):
    try:
        if not instance.prev_hash:
            try:
                last = AuditoriaGeneral.objects.order_by('-id').first()
                instance.prev_hash = getattr(last, 'hash_registro', None)
            except Exception:
                instance.prev_hash = None
        payload = {
            'tabla': instance.nombre_tabla or '',
            'registro': instance.id_registro_afectado or '',
            'op': instance.tipo_operacion or '',
            'usuario_id': getattr(instance.usuario, 'id', None),
            'fecha_evento': instance.fecha_evento.isoformat() if instance.fecha_evento else '',
            'antiguos': instance.datos_antiguos if instance.datos_antiguos is not None else None,
            'nuevos': instance.datos_nuevos if instance.datos_nuevos is not None else None,
            'prev_hash': instance.prev_hash or '',
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        instance.hash_registro = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    except Exception:
        pass
