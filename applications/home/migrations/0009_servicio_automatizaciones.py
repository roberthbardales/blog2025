from django.db import migrations

AUTOMATIZACION = {
    'nombre': 'Automatizaciones para tu Negocio',
    'descripcion': 'Un paquete que automatiza los procesos repetitivos de tu PYME: atención, recordatorios, reportes y ventas, para que te enfoques en crecer.',
    'caracteristicas': [
        'Bot de WhatsApp con atención 24/7',
        'Recordatorios automáticos de citas y pagos',
        'Reportes de ventas automáticos a tu correo',
        'Facturación electrónica integrada',
        'Recuperación de carritos abandonados',
    ],
    'icono': 'fas fa-robot',
    'color': 'purple',
    'orden': 10,
}


def crear_automatizacion(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    Servicio.objects.create(
        nombre=AUTOMATIZACION['nombre'],
        descripcion=AUTOMATIZACION['descripcion'],
        precio=None,
        caracteristicas=AUTOMATIZACION['caracteristicas'],
        icono=AUTOMATIZACION['icono'],
        color=AUTOMATIZACION['color'],
        destacado=False,
        activo=True,
        orden=AUTOMATIZACION['orden'],
    )


def eliminar_automatizacion(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    Servicio.objects.filter(nombre=AUTOMATIZACION['nombre']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_servicio_precios_parciales'),
    ]

    operations = [
        migrations.RunPython(crear_automatizacion, eliminar_automatizacion),
    ]
