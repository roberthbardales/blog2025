from django.db import migrations

CATALOGO = {
    'nombre': 'Catálogo Web',
    'descripcion': 'Catálogo digital para mostrar tus productos o servicios con pedidos por WhatsApp, sin necesidad de pasarela de pagos.',
    'caracteristicas': [
        'Catálogo de tus productos o servicios',
        'Fotos y descripciones',
        'Diseño responsive',
        'Botón de WhatsApp para pedidos',
        'Fácil de actualizar',
    ],
    'icono': 'fas fa-book-open',
    'color': 'slate',
    'orden': 3,
}


def crear_catalogo(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    Servicio.objects.create(
        nombre=CATALOGO['nombre'],
        descripcion=CATALOGO['descripcion'],
        precio=None,
        caracteristicas=CATALOGO['caracteristicas'],
        icono=CATALOGO['icono'],
        color=CATALOGO['color'],
        destacado=False,
        activo=True,
        orden=CATALOGO['orden'],
    )


def eliminar_catalogo(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    Servicio.objects.filter(nombre=CATALOGO['nombre']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_fusionar_ventas_inventario'),
    ]

    operations = [
        migrations.RunPython(crear_catalogo, eliminar_catalogo),
    ]
