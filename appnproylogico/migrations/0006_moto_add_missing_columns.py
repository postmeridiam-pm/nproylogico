from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('appnproylogico', '0005_motorista_add_nombres'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE moto
                ADD COLUMN IF NOT EXISTS propietario_tipo VARCHAR(9) NULL,
                ADD COLUMN IF NOT EXISTS propietario_tipo_documento VARCHAR(9) NOT NULL,
                ADD COLUMN IF NOT EXISTS propietario_documento VARCHAR(20) NOT NULL,
                ADD COLUMN IF NOT EXISTS motorista_propietario_id INT NULL,
                ADD COLUMN IF NOT EXISTS cilindrada_cc SMALLINT UNSIGNED NULL,
                ADD COLUMN IF NOT EXISTS color VARCHAR(30) NULL,
                ADD COLUMN IF NOT EXISTS tipo_combustible VARCHAR(9) NOT NULL,
                ADD COLUMN IF NOT EXISTS numero_motor VARCHAR(30) NOT NULL UNIQUE,
                ADD COLUMN IF NOT EXISTS numero_chasis VARCHAR(30) NOT NULL UNIQUE,
                ADD COLUMN IF NOT EXISTS fecha_inscripcion DATE NOT NULL,
                ADD COLUMN IF NOT EXISTS fecha_revision_tecnica DATE NULL,
                ADD COLUMN IF NOT EXISTS fecha_venc_permiso_circulacion DATE NULL,
                ADD COLUMN IF NOT EXISTS fecha_venc_seguro_soap DATE NULL,
                ADD COLUMN IF NOT EXISTS permiso_circulacion_anio SMALLINT UNSIGNED NULL,
                ADD COLUMN IF NOT EXISTS seguro_obligatorio_anio SMALLINT UNSIGNED NULL,
                ADD COLUMN IF NOT EXISTS revision_tecnica_anio SMALLINT UNSIGNED NULL,
                ADD COLUMN IF NOT EXISTS estado VARCHAR(10) NOT NULL,
                ADD COLUMN IF NOT EXISTS kilometraje_actual INT UNSIGNED NOT NULL DEFAULT 0,
                ADD COLUMN IF NOT EXISTS activo TINYINT(1) NOT NULL DEFAULT 1,
                ADD COLUMN IF NOT EXISTS fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS usuario_modificacion_id INT NULL
            """,
            reverse_sql="""
            ALTER TABLE moto
                DROP COLUMN IF EXISTS usuario_modificacion_id,
                DROP COLUMN IF EXISTS fecha_modificacion,
                DROP COLUMN IF EXISTS fecha_creacion,
                DROP COLUMN IF EXISTS activo,
                DROP COLUMN IF EXISTS kilometraje_actual,
                DROP COLUMN IF EXISTS estado,
                DROP COLUMN IF EXISTS revision_tecnica_anio,
                DROP COLUMN IF EXISTS seguro_obligatorio_anio,
                DROP COLUMN IF EXISTS permiso_circulacion_anio,
                DROP COLUMN IF EXISTS fecha_venc_seguro_soap,
                DROP COLUMN IF EXISTS fecha_venc_permiso_circulacion,
                DROP COLUMN IF EXISTS fecha_revision_tecnica,
                DROP COLUMN IF EXISTS fecha_inscripcion,
                DROP COLUMN IF EXISTS numero_chasis,
                DROP COLUMN IF EXISTS numero_motor,
                DROP COLUMN IF EXISTS tipo_combustible,
                DROP COLUMN IF EXISTS color,
                DROP COLUMN IF EXISTS cilindrada_cc,
                DROP COLUMN IF EXISTS motorista_propietario_id,
                DROP COLUMN IF EXISTS propietario_documento,
                DROP COLUMN IF EXISTS propietario_tipo_documento,
                DROP COLUMN IF EXISTS propietario_tipo
            """,
        ),
    ]

