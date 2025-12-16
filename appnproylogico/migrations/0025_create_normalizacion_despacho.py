from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('appnproylogico', '0024_localfarmacia_farm_lat_rango_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NormalizacionDespacho',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('fuente', models.CharField(max_length=50)),
                ('farmacia_origen_local_id', models.CharField(max_length=50, blank=True, null=True)),
                ('motorista_documento', models.CharField(max_length=50, blank=True, null=True)),
                ('cliente_nombre_raw', models.CharField(max_length=255, blank=True, null=True)),
                ('cliente_telefono_raw', models.CharField(max_length=50, blank=True, null=True)),
                ('destino_direccion_raw', models.CharField(max_length=255, blank=True, null=True)),
                ('destino_lat_raw', models.CharField(max_length=50, blank=True, null=True)),
                ('destino_lng_raw', models.CharField(max_length=50, blank=True, null=True)),
                ('estado_raw', models.CharField(max_length=50, blank=True, null=True)),
                ('tipo_despacho_raw', models.CharField(max_length=100, blank=True, null=True)),
                ('prioridad_raw', models.CharField(max_length=50, blank=True, null=True)),
                ('numero_receta_raw', models.CharField(max_length=100, blank=True, null=True)),
                ('observaciones_raw', models.TextField(blank=True, null=True)),
                ('fecha_registro_raw', models.CharField(max_length=50, blank=True, null=True)),
                ('procesado', models.BooleanField()),
                ('error_normalizacion', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField()),
            ],
            options={
                'db_table': 'normalizacion_despacho',
            },
        ),
    ]
