from django.core.management.base import BaseCommand, CommandError

from applications.empleos.services import (
    buscar_ofertas_automaticas,
    guardar_ofertas,
)

FILTROS_PREDEFINIDOS = {
    "search": ["python", "hacking", "django","linux","php","fastapi"],
    "country_id": 1,
    "from_age": 1,
    "type_order": 1,
    "job_seniority": [1, 2, 3],
}


class Command(BaseCommand):
    help = (
        "Busca ofertas en la API con filtros predefinidos y las guarda en la BD. "
        "Diseñado para ejecutarse cada hora (cron)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--keywords",
            nargs="*",
            dest="keywords",
            help="Palabras clave para sobrescribir las predefinidas.",
        )
        parser.add_argument(
            "--max-pages",
            type=int,
            default=3,
            help="Máximo de páginas a recorrer por keyword (default 3).",
        )

    def handle(self, *args, **options):
        filtros = dict(FILTROS_PREDEFINIDOS)
        if options.get("keywords"):
            filtros["search"] = options["keywords"]

        if not filtros.get("search"):
            raise CommandError("No hay palabras clave configuradas (filtros['search']).")

        max_pages = options["max_pages"]

        self.stdout.write(
            self.style.WARNING(
                f"Buscando ofertas con {len(filtros['search'])} keyword(s), "
                f"máximo {max_pages} páginas c/u ..."
            )
        )

        try:
            ofertas_api = buscar_ofertas_automaticas(filtros, max_pages=max_pages)
        except (ConnectionError, ValueError, RuntimeError) as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(f"Error inesperado: {e}")

        nuevas, existentes, _ = guardar_ofertas(ofertas_api)

        self.stdout.write(
            self.style.SUCCESS(
                f"Completado: {len(ofertas_api)} obtenidas, "
                f"{nuevas} nuevas, {existentes} ya existentes."
            )
        )