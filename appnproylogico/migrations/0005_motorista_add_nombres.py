from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('appnproylogico', '0004_motorista_add_missing_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE motorista
                ADD COLUMN IF NOT EXISTS nombres VARCHAR(100) NULL
            """,
            reverse_sql="""
            ALTER TABLE motorista
                DROP COLUMN IF EXISTS nombres
            """,
        ),
    ]

