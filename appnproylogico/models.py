from django.db import models

# Create your models here.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class AsignacionMotoMotorista(models.Model):
    id = models.AutoField(primary_key=True)
    motorista = models.ForeignKey('Motorista', models.DO_NOTHING, null=True, blank=True)
    moto = models.ForeignKey('Moto', models.DO_NOTHING, null=True, blank=True)
    fecha_asignacion = models.DateTimeField()
    fecha_desasignacion = models.DateTimeField(blank=True, null=True)
    kilometraje_inicio = models.PositiveIntegerField(db_comment='Kilometraje al iniciar turno')
    kilometraje_fin = models.PositiveIntegerField(blank=True, null=True, db_comment='Kilometraje al finalizar turno')
    activa = models.BooleanField(db_comment='Solo una asignación activa por moto')  
    observaciones = models.TextField(blank=True, null=True, db_comment='Notas sobre estado, incidentes, etc')

    class Meta:
        managed = True
        db_table = 'asignacion_moto_motorista'
        db_table_comment = 'Control temporal: qué motorista tiene qué moto en cada turno'
        indexes = [
            models.Index(fields=['moto','activa']),
            models.Index(fields=['motorista','activa']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(models.Q(kilometraje_fin__isnull=True) | models.Q(kilometraje_fin__gte=models.F('kilometraje_inicio'))),
                name='asig_km_fin_gte_inicio_or_null'
            ),
            models.CheckConstraint(
                check=(models.Q(activa=True) & models.Q(fecha_desasignacion__isnull=True)) | (models.Q(activa=False)),
                name='asig_activa_sin_desasignacion'
            ),
            models.UniqueConstraint(
                fields=['moto'],
                condition=models.Q(activa=True),
                name='uniq_asig_moto_activa'
            ),
            models.UniqueConstraint(
                fields=['motorista'],
                condition=models.Q(activa=True),
                name='uniq_asig_motorista_activa'
            ),
        ]


class AsignacionMotoristaFarmacia(models.Model):
    id = models.AutoField(primary_key=True)
    motorista = models.ForeignKey('Motorista', models.DO_NOTHING, null=True, blank=True)
    farmacia = models.ForeignKey('Localfarmacia', models.DO_NOTHING, db_column='farmacia_id', null=True, blank=True)
    fecha_asignacion = models.DateTimeField()
    fecha_desasignacion = models.DateTimeField(blank=True, null=True)
    activa = models.BooleanField()        
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'asignacion_motorista_farmacia'
        indexes = [
            models.Index(fields=['motorista','activa']),
            models.Index(fields=['farmacia','activa']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(models.Q(activa=True) & models.Q(fecha_desasignacion__isnull=True)) | (models.Q(activa=False)),
                name='asig_mf_activa_sin_desasignacion'
            ),
            models.UniqueConstraint(
                fields=['motorista','farmacia'],
                condition=models.Q(activa=True),
                name='uniq_asig_mf_activa'
            ),
        ]


class AuditoriaGeneral(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre_tabla = models.CharField(max_length=64, db_comment='Tabla donde ocurrió el evento (ej: usuario, moto)')
    id_registro_afectado = models.CharField(max_length=36, db_comment='ID del registro que fue modificado (PK de la tabla original)')
    tipo_operacion = models.CharField(max_length=6)
    usuario = models.ForeignKey('Usuario', models.DO_NOTHING, blank=True, null=True, db_comment='Usuario que realizó la acción (NULL si es acción del sistema)')        
    fecha_evento = models.DateTimeField()
    datos_antiguos = models.JSONField(blank=True, null=True, db_comment='Valores ANTES del cambio (NULL para INSERT)')        
    datos_nuevos = models.JSONField(blank=True, null=True, db_comment='Valores DESPUÉS del cambio (NULL para DELETE)')        
    prev_hash = models.CharField(max_length=64, blank=True, null=True)
    hash_registro = models.CharField(max_length=64, blank=True, null=True, unique=True)

    class Meta:
        managed = True
        db_table = 'auditoria_general'    
        db_table_comment = 'Auditoría inmutable de cambios en la base de datos'     

 


class Comuna(models.Model):
    id = models.SmallAutoField(primary_key=True)
    region = models.ForeignKey('Region', models.DO_NOTHING, null=True, blank=True)
    codigo = models.CharField(unique=True, max_length=10, db_comment='Código INE')  
    nombre = models.CharField(max_length=80)
    activo = models.BooleanField()        

    class Meta:
        managed = True
        db_table = 'comuna'
        db_table_comment = 'Comunas de Chile'

    def __str__(self):
        try:
            return f"{self.nombre}"
        except Exception:
            return super().__str__()


class Despacho(models.Model):
    id = models.BigAutoField(primary_key=True)
    codigo_despacho = models.CharField(unique=True, max_length=20, db_comment='ID visible: DSP-2025-000123')
    numero_orden_farmacia = models.CharField(max_length=50, blank=True, null=True, db_comment='Número de orden interna farmacia')
    farmacia_origen_local_id = models.CharField(max_length=20, db_comment='local_id de localfarmacia origen')
    farmacia_destino_local_id = models.CharField(max_length=20, blank=True, null=True, db_comment='local_id de localfarmacia destino (intercambios)')
    motorista = models.ForeignKey('Motorista', models.DO_NOTHING, null=True, blank=True)
    estado = models.CharField(max_length=12)
    tipo_despacho = models.CharField(max_length=27)
    prioridad = models.CharField(max_length=5)
    cliente_nombre = models.CharField(max_length=100, blank=True, null=True)        
    cliente_telefono = models.CharField(max_length=15, blank=True, null=True)       
    cliente_comuna_nombre = models.CharField(max_length=80, blank=True, null=True, db_comment='Comuna cliente (desnormalizado)')
    destino_direccion = models.CharField(max_length=200)
    destino_referencia = models.CharField(max_length=200, blank=True, null=True, db_comment='Referencias: "casa azul", "edificio X"')
    destino_lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, db_comment='GPS destino')       
    destino_lng = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, db_comment='GPS destino')       
    destino_geolocalizacion_validada = models.BooleanField(db_comment='Si coordenadas verificadas')
    tiene_receta_retenida = models.BooleanField()
    numero_receta = models.CharField(max_length=50, blank=True, null=True, db_comment='Número único de receta médica')        
    requiere_devolucion_receta = models.BooleanField(db_comment='Receta física debe volver')
    receta_devuelta_farmacia = models.BooleanField(db_comment='Confirmación devolución')
    fecha_devolucion_receta = models.DateTimeField(blank=True, null=True)
    quien_recibe_receta = models.CharField(max_length=100, blank=True, null=True, db_comment='Empleado farmacia que recibe')  
    observaciones_receta = models.TextField(blank=True, null=True, db_comment='ENCRYPTED by Django: Notas clínicas')
    descripcion_productos = models.TextField(db_comment='Detalle: "Paracetamol 500mg x2, ..."')
    valor_declarado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_comment='Valor total en CLP')
    requiere_aprobacion_operadora = models.BooleanField()
    aprobado_por_operadora = models.BooleanField()
    usuario_aprobador = models.ForeignKey('Usuario', models.DO_NOTHING, blank=True, null=True, db_comment='Supervisor que aprobó')
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    fecha_registro = models.DateTimeField()
    fecha_asignacion = models.DateTimeField(blank=True, null=True, db_comment='Cuando se asigna motorista')
    fecha_salida_farmacia = models.DateTimeField(blank=True, null=True, db_comment='Motorista confirma salida')
    fecha_llegada_destino = models.DateTimeField(blank=True, null=True, db_comment='Motorista confirma llegada')
    fecha_completado = models.DateTimeField(blank=True, null=True, db_comment='Entrega confirmada exitosa')
    fecha_anulacion = models.DateTimeField(blank=True, null=True, db_comment='Si se cancela')
    tiempo_total_minutos = models.PositiveIntegerField(blank=True, null=True, db_comment='Calculado automáticamente por trigger')
    receptor_nombre = models.CharField(max_length=100, blank=True, null=True)       
    receptor_tipo_documento = models.CharField(max_length=13, blank=True, null=True)
    receptor_documento = models.CharField(max_length=20, blank=True, null=True)     
    receptor_relacion = models.CharField(max_length=50, blank=True, null=True, db_comment='Titular/Familiar/Vecino/Otro')     
    firma_digital = models.BooleanField(db_comment='Firma electrónica capturada')   
    hubo_incidencia = models.BooleanField()
    tipo_incidencia = models.CharField(max_length=100, blank=True, null=True, db_comment='CLIENTE_AUSENTE, DIRECCION_INCORRECTA, etc')
    descripcion_incidencia = models.TextField(blank=True, null=True)
    tiempo_perdido_minutos = models.PositiveIntegerField(blank=True, null=True, db_comment='Tiempo adicional por incidencia') 
    observaciones = models.TextField(blank=True, null=True)
    motivo_anulacion = models.CharField(max_length=500, blank=True, null=True)      
    usuario_registro = models.ForeignKey('Usuario', models.DO_NOTHING, related_name='despacho_usuario_registro_set', blank=True, null=True, db_comment='Operadora que registró')
    usuario_modificacion = models.ForeignKey('Usuario', models.DO_NOTHING, related_name='despacho_usuario_modificacion_set', blank=True, null=True, db_comment='Último usuario que modificó')
    fecha_modificacion = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'despacho'
        db_table_comment = 'CORE: Entregas farmacéuticas. Datos salud encriptados. Geolocalización activa.'
        indexes = [
            models.Index(fields=['codigo_despacho']),
            models.Index(fields=['fecha_registro']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_despacho']),
            models.Index(fields=['farmacia_origen_local_id', 'fecha_registro']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(estado__in=['PENDIENTE','ASIGNADO','PREPARANDO','PREPARADO','EN_CAMINO','ENTREGADO','FALLIDO','ANULADO']),
                name='desp_estado_valido'
            ),
            models.CheckConstraint(
                check=(models.Q(destino_geolocalizacion_validada=False) | (models.Q(destino_lat__isnull=False) & models.Q(destino_lng__isnull=False))),
                name='desp_geo_valida_requiere_coord'
            ),
            models.CheckConstraint(
                check=(models.Q(receta_devuelta_farmacia=False) | models.Q(fecha_devolucion_receta__isnull=False)),
                name='desp_receta_devuelta_requiere_fecha'
            ),
            models.CheckConstraint(
                check=(models.Q(estado='ANULADO') & models.Q(motivo_anulacion__isnull=False) & models.Q(fecha_anulacion__isnull=False)) | ~models.Q(estado='ANULADO'),
                name='desp_anulado_requiere_motivo_y_fecha'
            ),
        ]


 


class Localfarmacia(models.Model):        
    id = models.AutoField(primary_key=True)
    local_id = models.CharField(max_length=20, unique=True, db_comment='ID original de la farmacia (756, 757, etc)')
    local_nombre = models.CharField(max_length=150)
    local_direccion = models.CharField(max_length=250)
    comuna_nombre = models.CharField(max_length=80)
    localidad_nombre = models.CharField(max_length=80)
    fk_region = models.ForeignKey('Region', models.DO_NOTHING, db_column='fk_region', blank=True, null=True, db_comment='Opcional: se asigna después de carga')
    fk_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='fk_comuna', blank=True, null=True, db_comment='Opcional: se asigna después de carga')
    fk_localidad = models.ForeignKey('Localidad', models.DO_NOTHING, db_column='fk_localidad', blank=True, null=True, db_comment='Opcional: se asigna después de carga')
    funcionamiento_hora_apertura = models.TimeField()
    funcionamiento_hora_cierre = models.TimeField()
    funcionamiento_dia = models.CharField(max_length=50, db_comment='lunes, martes, lun-vie, 24/7, etc')
    local_telefono = models.CharField(max_length=25, blank=True, null=True)
    local_lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, db_comment='Latitud GPS')
    local_lng = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, db_comment='Longitud GPS')        
    geolocalizacion_validada = models.BooleanField(db_comment='Si coordenadas fueron verificadas')
    fecha_geolocalizacion = models.DateTimeField(blank=True, null=True, db_comment='Cuándo se agregaron coordenadas')
    fecha = models.DateField(db_comment='Fecha de última actualización desde Excel')
    activo = models.BooleanField()        
    fecha_creacion = models.DateTimeField()
    fecha_modificacion = models.DateTimeField()
    usuario_modificacion = models.ForeignKey('Usuario', models.DO_NOTHING, blank=True, null=True, db_comment='ID del usuario que modificó por última vez')

    class Meta:
        managed = True
        db_table = 'localfarmacia'        
        db_table_comment = 'Farmacias Cruz Verde. Geolocalización activa para inserción directa.'
        indexes = []
        constraints = [
            models.CheckConstraint(
                check=(models.Q(local_lat__isnull=True) | (models.Q(local_lat__gte=-90) & models.Q(local_lat__lte=90))),
                name='farm_lat_rango'
            ),
            models.CheckConstraint(
                check=(models.Q(local_lng__isnull=True) | (models.Q(local_lng__gte=-180) & models.Q(local_lng__lte=180))),
                name='farm_lng_rango'
            ),
            models.CheckConstraint(
                check=(models.Q(geolocalizacion_validada=False) | (models.Q(local_lat__isnull=False) & models.Q(local_lng__isnull=False))),
                name='farm_geo_valida_requiere_coord'
            ),
        ]

    def __str__(self):
        try:
            return f"{self.local_nombre}"
        except Exception:
            return super().__str__()


class Localidad(models.Model):
    id = models.SmallAutoField(primary_key=True)
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING, null=True, blank=True)
    nombre = models.CharField(max_length=80)
    activo = models.BooleanField()        

    class Meta:
        managed = True
        db_table = 'localidad'
        db_table_comment = 'Localidades dentro de comunas'

    def __str__(self):
        try:
            return f"{self.nombre}"
        except Exception:
            return super().__str__()


class Moto(models.Model):
    id = models.AutoField(primary_key=True)
    patente = models.CharField(unique=True, max_length=7, db_comment='PPU Chile: AA1234 o ABCD12')
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveSmallIntegerField(blank=True, null=True, db_comment='Año fabricación')
    propietario_nombre = models.CharField(max_length=100)
    propietario_tipo = models.CharField(max_length=9, blank=True, null=True, db_comment='EMPRESA o MOTORISTA')
    propietario_tipo_documento = models.CharField(max_length=9)
    propietario_documento = models.CharField(max_length=20)
    motorista_propietario = models.ForeignKey('Motorista', models.DO_NOTHING, blank=True, null=True, db_comment='Si propietario es MOTORISTA, referencia a la persona')
    cilindrada_cc = models.PositiveSmallIntegerField(blank=True, null=True, db_comment='Cilindrada en cc')
    color = models.CharField(max_length=30, blank=True, null=True)
    tipo_combustible = models.CharField(max_length=9)
    numero_motor = models.CharField(unique=True, max_length=30)
    numero_chasis = models.CharField(unique=True, max_length=30)
    fecha_inscripcion = models.DateField(db_comment='Inscripción Registro Civil')   
    fecha_revision_tecnica = models.DateField(blank=True, null=True, db_comment='Última revisión técnica')
    fecha_venc_permiso_circulacion = models.DateField(blank=True, null=True, db_comment='Vencimiento permiso municipal')      
    fecha_venc_seguro_soap = models.DateField(blank=True, null=True, db_comment='Vencimiento SOAP (obligatorio)')
    permiso_circulacion_anio = models.PositiveSmallIntegerField(blank=True, null=True, db_comment='Año del permiso de circulación vigente')
    seguro_obligatorio_anio = models.PositiveSmallIntegerField(blank=True, null=True, db_comment='Año del seguro obligatorio vigente')
    revision_tecnica_anio = models.PositiveSmallIntegerField(blank=True, null=True, db_comment='Año de la revisión técnica vigente')
    estado = models.CharField(max_length=10)
    kilometraje_actual = models.PositiveIntegerField()
    activo = models.BooleanField()        
    fecha_creacion = models.DateTimeField()
    fecha_modificacion = models.DateTimeField()
    usuario_modificacion = models.ForeignKey('Usuario', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'moto'
        db_table_comment = 'Motos con documentación legal chilena completa'
        constraints = [
            models.CheckConstraint(
                check=models.Q(propietario_tipo__in=['EMPRESA','MOTORISTA']) | models.Q(propietario_tipo__isnull=True),
                name='moto_propietario_tipo_valido'
            ),
            models.CheckConstraint(
                check=models.Q(estado__in=['OPERATIVO','OCUPADO','EN_TALLER','FUERA_DE_SERVICIO','EN_MANTENIMIENTO']),
                name='moto_estado_valido'
            ),
            models.CheckConstraint(
                check=models.Q(tipo_combustible__in=['BENCINA','DIESEL','GNC','GLP','ELECTRICO','HIBRIDO']),
                name='moto_combustible_valido'
            ),
        ]

    def __str__(self):
        try:
            return f"{self.patente}"
        except Exception:
            return super().__str__()


class Motorista(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField('Usuario', models.DO_NOTHING, blank=True, null=True, db_comment='Herencia 1:1 con usuario')
    codigo_motorista = models.CharField(max_length=20, unique=True, blank=True, null=True, db_comment='Código interno del motorista')
    nombres = models.CharField(max_length=100, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=50, blank=True, null=True)
    apellido_materno = models.CharField(max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    comuna_nombre = models.CharField(max_length=80, blank=True, null=True)
    provincia_nombre = models.CharField(max_length=80, blank=True, null=True)
    region_nombre = models.CharField(max_length=80, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    licencia_numero = models.CharField(max_length=20)
    licencia_clase = models.CharField(max_length=5, db_comment='Clase A requerida para motos')
    fecha_vencimiento_licencia = models.DateField()
    emergencia_nombre = models.CharField(max_length=100)
    emergencia_telefono = models.CharField(max_length=15)
    emergencia_parentesco = models.CharField(max_length=50)
    emergencias = models.JSONField(blank=True, null=True, db_comment='Lista de contactos de emergencia adicionales (1–5)')
    incluye_moto_personal = models.BooleanField(default=False, db_comment='El motorista posee moto propia')
    licencia_fecha_ultimo_control = models.DateField(blank=True, null=True)
    licencia_fecha_control = models.DateField(blank=True, null=True)
    licencia_archivo_path = models.CharField(max_length=200, blank=True, null=True, db_comment='Ruta del archivo de licencia almacenado en MEDIA')
    total_entregas_completadas = models.PositiveIntegerField()
    total_entregas_fallidas = models.PositiveIntegerField()
    activo = models.BooleanField()        
    disponible_hoy = models.BooleanField(db_comment='Disponibilidad del día actual')
    fecha_creacion = models.DateTimeField()
    fecha_modificacion = models.DateTimeField()
    usuario_modificacion = models.ForeignKey('Usuario', models.DO_NOTHING, related_name='motorista_usuario_modificacion_set', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'motorista'
        db_table_comment = 'Motoristas: especialización de usuario con licencia clase A'

    def __str__(self):
        try:
            return f"{self.usuario.nombre} {self.usuario.apellido}".strip()
        except Exception:
            return super().__str__()


class MovimientoDespacho(models.Model):   
    id = models.BigAutoField(primary_key=True)
    despacho = models.ForeignKey(Despacho, models.DO_NOTHING, blank=True, null=True)
    estado_anterior = models.CharField(max_length=12, blank=True, null=True, db_comment='Estado previo')
    estado_nuevo = models.CharField(max_length=12, db_comment='Estado después del cambio')
    fecha_movimiento = models.DateTimeField()
    usuario = models.ForeignKey('Usuario', models.DO_NOTHING, blank=True, null=True, db_comment='Quien registró el cambio (operadora por radio)')    
    motorista_lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, db_comment='GPS motorista al momento del cambio')
    motorista_lng = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, db_comment='GPS motorista al momento del cambio')
    observacion = models.TextField(blank=True, null=True, db_comment='Notas adicionales del cambio de estado')

    class Meta:
        managed = True
        db_table = 'movimiento_despacho'  
        db_table_comment = 'INMUTABLE: Historial completo de cambios de estado. Geolocalización activa.'
        indexes = [
            models.Index(fields=['fecha_movimiento']),
            models.Index(fields=['estado_nuevo']),
            models.Index(fields=['despacho', 'fecha_movimiento']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(estado_nuevo__in=['PENDIENTE','ASIGNADO','PREPARANDO','PREPARADO','EN_CAMINO','ENTREGADO','FALLIDO','ANULADO']),
                name='mov_estado_nuevo_valido'
            ),
            models.CheckConstraint(
                check=models.Q(estado_anterior__in=['PENDIENTE','ASIGNADO','PREPARANDO','PREPARADO','EN_CAMINO','ENTREGADO','FALLIDO','ANULADO']) | models.Q(estado_anterior__isnull=True),
                name='mov_estado_anterior_valido_o_null'
            ),
            models.CheckConstraint(
                check=~models.Q(estado_anterior=models.F('estado_nuevo')),
                name='mov_estado_no_igual'
            ),
        ]


 


class Region(models.Model):
    id = models.SmallAutoField(primary_key=True)
    codigo = models.CharField(unique=True, max_length=5, db_comment='Código INE')   
    nombre = models.CharField(max_length=50)
    activo = models.BooleanField()        

    class Meta:
        managed = True
        db_table = 'region'
        db_table_comment = 'Regiones de Chile'

    def __str__(self):
        try:
            return f"{self.nombre}"
        except Exception:
            return super().__str__()


class Rol(models.Model):
    id = models.SmallAutoField(primary_key=True)
    codigo = models.CharField(unique=True, max_length=20)
    nombre = models.CharField(max_length=50)
    django_group_name = models.CharField(max_length=150, db_comment='Nombre del Group en auth_group de Django')
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    activo = models.BooleanField()        
    fecha_creacion = models.DateTimeField()
    fecha_modificacion = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'rol'
        db_table_comment = 'Roles de negocio mapeados a Django Groups para permisos'


 


    


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    rol = models.ForeignKey(Rol, models.DO_NOTHING, null=True, blank=True)
    django_user_id = models.IntegerField(unique=True, db_comment='FK a auth_user.id de Django')
    tipo_documento = models.CharField(max_length=13)
    documento_identidad = models.CharField(unique=True, max_length=20)
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=80)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    activo = models.BooleanField()        
    fecha_creacion = models.DateTimeField()
    fecha_modificacion = models.DateTimeField()
    usuario_modificacion = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True, db_comment='ID del usuario que modificó por última vez')
    consiente_datos_salud = models.BooleanField(default=False)
    fecha_consentimiento_salud = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usuario'
        db_table_comment = 'Extiende Django User con datos de negocio. Permisos via Django Groups'


class NormalizacionDespacho(models.Model):
    id = models.BigAutoField(primary_key=True)
    fuente = models.CharField(max_length=50)
    farmacia_origen_local_id = models.CharField(max_length=50, blank=True, null=True)
    motorista_documento = models.CharField(max_length=50, blank=True, null=True)
    cliente_nombre_raw = models.CharField(max_length=255, blank=True, null=True)
    cliente_telefono_raw = models.CharField(max_length=50, blank=True, null=True)
    destino_direccion_raw = models.CharField(max_length=255, blank=True, null=True)
    destino_lat_raw = models.CharField(max_length=50, blank=True, null=True)
    destino_lng_raw = models.CharField(max_length=50, blank=True, null=True)
    estado_raw = models.CharField(max_length=50, blank=True, null=True)
    tipo_despacho_raw = models.CharField(max_length=100, blank=True, null=True)
    prioridad_raw = models.CharField(max_length=50, blank=True, null=True)
    numero_receta_raw = models.CharField(max_length=100, blank=True, null=True)
    observaciones_raw = models.TextField(blank=True, null=True)
    fecha_registro_raw = models.CharField(max_length=50, blank=True, null=True)
    procesado = models.BooleanField()
    error_normalizacion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'normalizacion_despacho'
