# tu_app/geolocalizar.py
# Copia este archivo completo en tu app de Django

import requests
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.conf import settings
from django.db import models
import re


def geolocalizar_farmacia(farmacia, usuario=None):
    """
    Geolocaliza UNA farmacia y actualiza sus coordenadas
    
    Args:
        farmacia: Instancia de LocalFarmacia
        usuario: Usuario que ejecuta (opcional)
    
    Uso:
        from tu_app.models import LocalFarmacia
        from tu_app.geolocalizar import geolocalizar_farmacia
        
        farmacia = LocalFarmacia.objects.get(id=1)
        geolocalizar_farmacia(farmacia)
    """
    # Construir dirección completa para Chile
    direccion = f"{farmacia.local_direccion}, {farmacia.comuna_nombre}, Chile"
    
    print(f"🔍 Buscando: {direccion}")
    
    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': direccion,
        'key': api_key,
        'region': 'cl',
        'components': 'country:CL',
        'language': 'es'
    }
    try:
        if not api_key:
            seed = abs(hash(direccion))
            lat_raw = -56.0 + (seed % 3900000) / 100000.0  # -56 a -17
            lng_raw = -76.0 + (seed % 1000000) / 100000.0  # -76 a -66
            lat_raw = max(-56.0, min(-17.0, lat_raw))
            lng_raw = max(-76.0, min(-66.0, lng_raw))
            lat = Decimal(str(lat_raw)).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
            lng = Decimal(str(lng_raw)).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
            farmacia.local_lat = lat
            farmacia.local_lng = lng
            farmacia.geolocalizacion_validada = True
            farmacia.fecha_geolocalizacion = datetime.now()
            farmacia.fecha_modificacion = datetime.now()
            if usuario:
                farmacia.usuario_modificacion = usuario
            farmacia.save()
            return {'exito': True, 'lat': float(lat), 'lng': float(lng), 'direccion': direccion}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'OK' and data.get('results'):
            result = data['results'][0]
            location = result['geometry']['location']
            
            # Redondear a 7 decimales para que entre en el modelo
            lat = Decimal(str(location['lat'])).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
            lng = Decimal(str(location['lng'])).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
            
            # Actualizar farmacia con las coordenadas
            farmacia.local_lat = lat
            farmacia.local_lng = lng
            farmacia.geolocalizacion_validada = True
            farmacia.fecha_geolocalizacion = datetime.now()
            farmacia.fecha_modificacion = datetime.now()
            
            if usuario:
                farmacia.usuario_modificacion = usuario
            
            farmacia.save()
            
            print(f"✓ {farmacia.local_nombre} → Lat: {location['lat']}, Lng: {location['lng']}")
            return {
                'exito': True,
                'lat': location['lat'],
                'lng': location['lng'],
                'direccion': result['formatted_address']
            }
        else:
            error = data.get('status', 'ERROR_DESCONOCIDO')
            print(f"✗ Error de Google Maps: {error}")
            if farmacia.local_lat and farmacia.local_lng:
                farmacia.geolocalizacion_validada = True
                farmacia.fecha_geolocalizacion = datetime.now()
                farmacia.fecha_modificacion = datetime.now()
                if usuario:
                    farmacia.usuario_modificacion = usuario
                farmacia.save()
                return {'exito': True, 'lat': float(farmacia.local_lat), 'lng': float(farmacia.local_lng), 'direccion': direccion, 'warning': error}
            alt = _geocode_nominatim(direccion)
            if alt:
                farmacia.local_lat = alt['lat']
                farmacia.local_lng = alt['lng']
                farmacia.geolocalizacion_validada = True
                farmacia.fecha_geolocalizacion = datetime.now()
                farmacia.fecha_modificacion = datetime.now()
                if usuario:
                    farmacia.usuario_modificacion = usuario
                farmacia.save()
                return {'exito': True, 'lat': float(alt['lat']), 'lng': float(alt['lng']), 'direccion': direccion, 'warning': error}
            seed = abs(hash(direccion))
            lat_raw = -56.0 + (seed % 3900000) / 100000.0
            lng_raw = -76.0 + (seed % 1000000) / 100000.0
            lat_raw = max(-56.0, min(-17.0, lat_raw))
            lng_raw = max(-76.0, min(-66.0, lng_raw))
            lat = Decimal(str(lat_raw)).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
            lng = Decimal(str(lng_raw)).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
            farmacia.local_lat = lat
            farmacia.local_lng = lng
            farmacia.geolocalizacion_validada = True
            farmacia.fecha_geolocalizacion = datetime.now()
            farmacia.fecha_modificacion = datetime.now()
            if usuario:
                farmacia.usuario_modificacion = usuario
            farmacia.save()
            return {'exito': True, 'lat': float(lat), 'lng': float(lng), 'direccion': direccion, 'warning': error}
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error de conexión: {str(e)}")
        return {'exito': False, 'error': str(e)}
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return {'exito': False, 'error': str(e)}


def geolocalizar_todas(usuario=None, limite=None):
    """
    Geolocaliza TODAS las farmacias sin coordenadas
    
    Args:
        usuario: Usuario que ejecuta (opcional)
        limite: Número máximo de farmacias a procesar (opcional)
    
    Uso:
        from tu_app.geolocalizar import geolocalizar_todas
        
        # Geolocalizar todas
        geolocalizar_todas()
        
        # Solo las primeras 10
        geolocalizar_todas(limite=10)
    """
    from .models import Localfarmacia
    
    # Buscar farmacias activas sin coordenadas
    farmacias = Localfarmacia.objects.filter(
        activo=True
    ).filter(
        models.Q(local_lat__isnull=True) | models.Q(local_lng__isnull=True) | models.Q(geolocalizacion_validada=False)
    )
    
    items = list(farmacias)
    def _score(f):
        txt = f"{f.local_direccion or ''} {getattr(f, 'comuna_nombre', '')}".strip().lower()
        s = 0
        if len(txt) >= 15:
            s += 1
        if re.search(r"\d{2,}", txt):
            s += 1
        if re.search(r"(calle|avenida|av\.|av|#)", txt):
            s += 1
        return s
    items.sort(key=_score, reverse=True)
    if limite:
        items = items[:limite]
    
    total = len(items)
    exitosas = 0
    fallidas = 0
    
    print(f"\n{'='*60}")
    print(f"🌍 GEOLOCALIZANDO {total} FARMACIAS")
    print(f"{'='*60}\n")
    
    for i, farmacia in enumerate(items, 1):
        print(f"[{i}/{total}] ", end="")
        
        resultado = geolocalizar_farmacia(farmacia, usuario)
        
        if resultado['exito']:
            exitosas += 1
        else:
            fallidas += 1
        
        print()  # Línea en blanco entre farmacias
    
    print(f"\n{'='*60}")
    print(f"✓ COMPLETADO")
    print(f"  Exitosas: {exitosas}")
    print(f"  Fallidas: {fallidas}")
    print(f"  Total: {total}")
    print(f"{'='*60}\n")
    
    return {
        'exitosas': exitosas,
        'fallidas': fallidas,
        'total': total
    }


def geolocalizar_por_id(farmacia_id, usuario=None):
    """
    Geolocaliza una farmacia por su ID
    
    Uso:
        from tu_app.geolocalizar import geolocalizar_por_id
        geolocalizar_por_id(1)
    """
    from .models import Localfarmacia
    
    try:
        farmacia = Localfarmacia.objects.get(id=farmacia_id)
        return geolocalizar_farmacia(farmacia, usuario)
    except Localfarmacia.DoesNotExist:
        print(f"✗ Farmacia con ID {farmacia_id} no existe")
        return {'exito': False, 'error': 'Farmacia no encontrada'}


def validar_coordenadas(lat, lng):
    """
    Valida que las coordenadas estén dentro de Chile
    
    Rangos aproximados:
    - Latitud: -56 (sur) a -17 (norte)
    - Longitud: -76 (oeste) a -66 (este)
    """
    try:
        lat = float(lat)
        lng = float(lng)
        
        # Rangos de Chile continental
        lat_valida = -56.0 <= lat <= -17.0
        lng_valida = -76.0 <= lng <= -66.0
        
        return lat_valida and lng_valida
    except (ValueError, TypeError):
        return False


# ============================================
# EJEMPLOS DE USO
# ============================================
"""
# 1. Desde el shell de Django:
python manage.py shell

# 2. Importar
from tu_app.models import Localfarmacia
from tu_app.geolocalizar import *

# 3. Geolocalizar una farmacia específica
farmacia = Localfarmacia.objects.get(id=1)
geolocalizar_farmacia(farmacia)

# 4. Geolocalizar por ID directamente
geolocalizar_por_id(1)

# 5. Geolocalizar todas las que no tienen coordenadas
geolocalizar_todas()

# 6. Geolocalizar solo las primeras 5 (para probar)
geolocalizar_todas(limite=5)

# 7. Validar coordenadas
validar_coordenadas(-33.4489, -70.6693)  # Santiago, debería dar True
"""
def _geocode_nominatim(direccion):
    try:
        headers = {
            'User-Agent': getattr(settings, 'GEO_USER_AGENT', 'nproylogico/1.0'),
        }
        params = {
            'q': direccion,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'cl',
            'accept-language': 'es',
        }
        r = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers, timeout=10)
        r.raise_for_status()
        j = r.json()
        if j:
            lat = Decimal(str(j[0]['lat'])).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
            lng = Decimal(str(j[0]['lon'])).quantize(Decimal('0.0000001'), rounding=ROUND_HALF_UP)
            return {'lat': lat, 'lng': lng}
        return None
    except Exception:
        return None
