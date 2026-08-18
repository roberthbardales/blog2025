from django.db import migrations

COLORES = {
    'Página Web Corporativa': 'blue',
    'Catálogo Web': 'teal',
    'Reservas y Citas': 'amber',
    'Tienda Online (E-commerce)': 'indigo',
    'Sistema de Ventas e Inventario': 'emerald',
    'Soporte Técnico Online': 'slate',
    'Automatizaciones para tu Negocio': 'purple',
}


def reorganizar_colores(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    for nombre, color in COLORES.items():
        Servicio.objects.filter(nombre=nombre).update(color=color)


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_servicio_catalogo_web'),
    ]

    operations = [
        migrations.RunPython(reorganizar_colores, migrations.RunPython.noop),
    ]
