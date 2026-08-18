import re

from django.db import migrations

PATRON_SOPORTE = re.compile(r'^\d+\s+(semana|semanas|mes|meses)\s+de\s+soporte$', re.IGNORECASE)


def quitar_tiempo_soporte(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    for servicio in Servicio.objects.all():
        nuevas = [f for f in servicio.caracteristicas if not PATRON_SOPORTE.match(f)]
        if len(nuevas) != len(servicio.caracteristicas):
            servicio.caracteristicas = nuevas
            servicio.save()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_servicio_automatizaciones'),
    ]

    operations = [
        migrations.RunPython(quitar_tiempo_soporte, migrations.RunPython.noop),
    ]
