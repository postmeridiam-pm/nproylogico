from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('appnproylogico', '0008_auditoria_worm_hash_triggers'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            UPDATE localfarmacia
            SET geolocalizacion_validada = 0
            WHERE geolocalizacion_validada = 1
              AND (local_lat IS NULL OR local_lng IS NULL);
            """,
            reverse_sql="""
            /* no-op reverse */
            """
        ),
        migrations.RunSQL(
            sql="""
            UPDATE localfarmacia
            SET geolocalizacion_validada = 0,
                local_lat = NULL
            WHERE local_lat IS NOT NULL
              AND (local_lat < -90 OR local_lat > 90);
            """,
            reverse_sql="""
            /* no-op reverse */
            """
        ),
        migrations.RunSQL(
            sql="""
            UPDATE localfarmacia
            SET geolocalizacion_validada = 0,
                local_lng = NULL
            WHERE local_lng IS NOT NULL
              AND (local_lng < -180 OR local_lng > 180);
            """,
            reverse_sql="""
            /* no-op reverse */
            """
        ),
    ]
