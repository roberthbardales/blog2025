from django.db import migrations

CARACTERISTICAS_ORIGINALES_VENTAS = [
    'Punto de venta',
    'Facturación y boletas',
    'Registro de clientes',
    'Stock de productos',
    'Reportes de ventas',
]

CARACTERISTICAS_ORIGINALES_INVENTARIO = [
    'Control de stock',
    'Múltiples almacenes',
    'Alertas de stock mínimo',
    'Órdenes de compra',
    'Reportes',
]

CARACTERISTICAS_FUSIONADAS = [
    'Punto de venta',
    'Facturación y boletas',
    'Registro de clientes',
    'Control de stock y múltiples almacenes',
    'Alertas de stock mínimo',
    'Órdenes de compra',
    'Reportes de ventas',
]


def fusionar(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    ventas = Servicio.objects.filter(nombre='Sistema de Ventas').first()
    if ventas:
        ventas.nombre = 'Sistema de Ventas e Inventario'
        ventas.descripcion = 'Sistema completo de ventas e inventario para controlar tu negocio en un solo lugar.'
        ventas.caracteristicas = CARACTERISTICAS_FUSIONADAS
        ventas.save()
    Servicio.objects.filter(nombre='Sistema de Inventario').delete()


def separar(apps, schema_editor):
    Servicio = apps.get_model('home', 'Servicio')
    fusionado = Servicio.objects.filter(nombre='Sistema de Ventas e Inventario').first()
    if fusionado:
        fusionado.nombre = 'Sistema de Ventas'
        fusionado.descripcion = 'Sistema de ventas con facturación, clientes, stock y reportes para tu negocio.'
        fusionado.caracteristicas = CARACTERISTICAS_ORIGINALES_VENTAS
        fusionado.save()
        Servicio.objects.create(
            nombre='Sistema de Inventario',
            descripcion='Control de stock, almacenes y órdenes de compra para tu negocio.',
            precio=None,
            caracteristicas=CARACTERISTICAS_ORIGINALES_INVENTARIO,
            icono='fas fa-boxes',
            color='blue',
            destacado=False,
            activo=True,
            orden=3,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_servicio_quitar_soporte'),
    ]

    operations = [
        migrations.RunPython(fusionar, separar),
    ]
