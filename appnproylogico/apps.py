from django.apps import AppConfig
import sys


class AppnproylogicoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appnproylogico'

    def ready(self):
        try:
            args = set(sys.argv or [])
            if any(a in args for a in {'makemigrations','migrate','collectstatic','test'}):
                return
            from . import signals
            from django.core.management import call_command
            from django.apps import apps
            from django.db import OperationalError
            Moto = apps.get_model('appnproylogico','Moto')
            Localfarmacia = apps.get_model('appnproylogico','Localfarmacia')
            Motorista = apps.get_model('appnproylogico','Motorista')
            try:
                motos = Moto.objects.count()
                farm = Localfarmacia.objects.count()
                mots = Motorista.objects.count()
            except OperationalError:
                return
            if motos < 210 or farm == 0 or mots < 200:
                try:
                    call_command('load_samples')
                except Exception:
                    pass
            import json, hashlib, pathlib, os
            from django.conf import settings as djset
            data_path = pathlib.Path(__file__).resolve().parent.parent / 'static' / 'data'
            targets = [
                'farmacias.json',
                'motoristas.json',
                'motos.json',
                'asignaciones_moto_motorista.json',
                'asignaciones_motorista_farmacia.json',
            ]
            sums = {}
            for name in targets:
                p = data_path / name
                if p.exists():
                    try:
                        b = p.read_bytes()
                        sums[name] = hashlib.sha1(b).hexdigest()
                    except Exception:
                        sums[name] = ''
            stamp_dir = pathlib.Path(djset.MEDIA_ROOT) / 'ingesta'
            os.makedirs(stamp_dir, exist_ok=True)
            stamp_file = stamp_dir / 'checksums.json'
            prev = {}
            if stamp_file.exists():
                try:
                    prev = json.loads(stamp_file.read_text(encoding='utf-8') or '{}')
                except Exception:
                    prev = {}
            if sums and sums != prev:
                try:
                    call_command('load_samples')
                except Exception:
                    pass
                try:
                    stamp_file.write_text(json.dumps(sums, ensure_ascii=False, indent=2), encoding='utf-8')
                except Exception:
                    pass
        except Exception:
            pass
