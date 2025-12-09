from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('appnproylogico', '0003_remove_despacho_medico_nombre_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE motorista
                ADD COLUMN IF NOT EXISTS codigo_motorista VARCHAR(20) NULL UNIQUE,
                ADD COLUMN IF NOT EXISTS apellido_paterno VARCHAR(50) NULL,
                ADD COLUMN IF NOT EXISTS apellido_materno VARCHAR(50) NULL,
                ADD COLUMN IF NOT EXISTS fecha_nacimiento DATE NULL,
                ADD COLUMN IF NOT EXISTS direccion VARCHAR(200) NULL,
                ADD COLUMN IF NOT EXISTS comuna_nombre VARCHAR(80) NULL,
                ADD COLUMN IF NOT EXISTS provincia_nombre VARCHAR(80) NULL,
                ADD COLUMN IF NOT EXISTS region_nombre VARCHAR(80) NULL,
                ADD COLUMN IF NOT EXISTS telefono VARCHAR(15) NULL,
                ADD COLUMN IF NOT EXISTS email VARCHAR(254) NULL,
                ADD COLUMN IF NOT EXISTS licencia_numero VARCHAR(20) NOT NULL,
                ADD COLUMN IF NOT EXISTS licencia_clase VARCHAR(5) NOT NULL,
                ADD COLUMN IF NOT EXISTS fecha_vencimiento_licencia DATE NOT NULL,
                ADD COLUMN IF NOT EXISTS emergencia_nombre VARCHAR(100) NOT NULL,
                ADD COLUMN IF NOT EXISTS emergencia_telefono VARCHAR(15) NOT NULL,
                ADD COLUMN IF NOT EXISTS emergencia_parentesco VARCHAR(50) NOT NULL,
                ADD COLUMN IF NOT EXISTS emergencias JSON NULL,
                ADD COLUMN IF NOT EXISTS incluye_moto_personal TINYINT(1) NOT NULL DEFAULT 0,
                ADD COLUMN IF NOT EXISTS licencia_fecha_ultimo_control DATE NULL,
                ADD COLUMN IF NOT EXISTS licencia_fecha_control DATE NULL,
                ADD COLUMN IF NOT EXISTS licencia_archivo_path VARCHAR(200) NULL,
                ADD COLUMN IF NOT EXISTS total_entregas_completadas INT UNSIGNED NOT NULL DEFAULT 0,
                ADD COLUMN IF NOT EXISTS total_entregas_fallidas INT UNSIGNED NOT NULL DEFAULT 0,
                ADD COLUMN IF NOT EXISTS activo TINYINT(1) NOT NULL DEFAULT 1,
                ADD COLUMN IF NOT EXISTS disponible_hoy TINYINT(1) NOT NULL DEFAULT 0,
                ADD COLUMN IF NOT EXISTS fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN IF NOT EXISTS usuario_modificacion_id INT NULL
            """,
            reverse_sql="""
            ALTER TABLE motorista
                DROP COLUMN IF EXISTS usuario_modificacion_id,
                DROP COLUMN IF EXISTS fecha_modificacion,
                DROP COLUMN IF EXISTS fecha_creacion,
                DROP COLUMN IF EXISTS disponible_hoy,
                DROP COLUMN IF EXISTS activo,
                DROP COLUMN IF EXISTS total_entregas_fallidas,
                DROP COLUMN IF EXISTS total_entregas_completadas,
                DROP COLUMN IF EXISTS licencia_archivo_path,
                DROP COLUMN IF EXISTS licencia_fecha_control,
                DROP COLUMN IF EXISTS licencia_fecha_ultimo_control,
                DROP COLUMN IF EXISTS incluye_moto_personal,
                DROP COLUMN IF EXISTS emergencias,
                DROP COLUMN IF EXISTS emergencia_parentesco,
                DROP COLUMN IF EXISTS emergencia_telefono,
                DROP COLUMN IF EXISTS emergencia_nombre,
                DROP COLUMN IF EXISTS fecha_vencimiento_licencia,
                DROP COLUMN IF EXISTS licencia_clase,
                DROP COLUMN IF EXISTS licencia_numero,
                DROP COLUMN IF EXISTS email,
                DROP COLUMN IF EXISTS telefono,
                DROP COLUMN IF EXISTS region_nombre,
                DROP COLUMN IF EXISTS provincia_nombre,
                DROP COLUMN IF EXISTS comuna_nombre,
                DROP COLUMN IF EXISTS direccion,
                DROP COLUMN IF EXISTS fecha_nacimiento,
                DROP COLUMN IF EXISTS apellido_materno,
                DROP COLUMN IF EXISTS apellido_paterno,
                DROP COLUMN IF EXISTS codigo_motorista
            """,
        ),
    ]

