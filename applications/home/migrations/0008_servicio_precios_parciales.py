from django.db import migrations

SIN_PRECIO = [
    'Sistema de Ventas',
    'Sistema de Inventario',
    'Reservas y Citas',
    'Tienda Online (E-commerce)',
]


def sin_precio(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    Servicio.objects.filter(nombre__in=SIN_PRECIO).update(precio=None)


def con_precio(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    Servicio.objects.filter(nombre__in=SIN_PRECIO).update(precio=0)


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_alter_servicio_precio'),
    ]

    operations = [
        migrations.RunPython(sin_precio, con_precio),
    ]
