from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('appnproylogico', '0007_despacho_despacho_codigo__20a9f7_idx_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE auditoria_general
                        ADD COLUMN IF NOT EXISTS prev_hash VARCHAR(64) NULL,
                        ADD COLUMN IF NOT EXISTS hash_registro VARCHAR(64) NULL;
                    """,
                    reverse_sql="""
                    ALTER TABLE auditoria_general
                        DROP COLUMN IF EXISTS hash_registro,
                        DROP COLUMN IF EXISTS prev_hash;
                    """
                ),
                migrations.RunSQL(
                    sql="""
                    DROP TRIGGER IF EXISTS auditoria_prevent_update;
                    CREATE TRIGGER auditoria_prevent_update BEFORE UPDATE ON auditoria_general
                    FOR EACH ROW BEGIN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'auditoria_general es WORM: UPDATE prohibido';
                    END;
                    """,
                    reverse_sql="""
                    DROP TRIGGER IF EXISTS auditoria_prevent_update;
                    """
                ),
                migrations.RunSQL(
                    sql="""
                    DROP TRIGGER IF EXISTS auditoria_prevent_delete;
                    CREATE TRIGGER auditoria_prevent_delete BEFORE DELETE ON auditoria_general
                    FOR EACH ROW BEGIN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'auditoria_general es WORM: DELETE prohibido';
                    END;
                    """,
                    reverse_sql="""
                    DROP TRIGGER IF EXISTS auditoria_prevent_delete;
                    """
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='auditoriageneral',
                    name='prev_hash',
                    field=models.CharField(max_length=64, blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='auditoriageneral',
                    name='hash_registro',
                    field=models.CharField(max_length=64, blank=True, null=True, unique=True),
                ),
            ],
        ),
    ]
