from django.core.management.base import BaseCommand, CommandError

from applications.empleos.models import FiltroEmpleo
from applications.empleos.services import (
    buscar_ofertas_automaticas,
    enviar_email_ofertas,
    enviar_telegram,
    guardar_ofertas,
    _resumen_nuevas,
)


def _filtros_desde_modelo(filtro: FiltroEmpleo) -> dict:
    filtros = {}
    if filtro.keywords:
        filtros["search"] = [k.strip() for k in filtro.keywords.split(",") if k.strip()]
    if filtro.country_id:
        filtros["country_id"] = filtro.country_id
    if filtro.from_age:
        filtros["from_age"] = filtro.from_age
    if filtro.type_order:
        filtros["type_order"] = filtro.type_order
    if filtro.job_seniority:
        filtros["job_seniority"] = filtro.job_seniority
    if filtro.work_modality_id:
        filtros["work_modality_id"] = filtro.work_modality_id
    if filtro.job_category_id:
        filtros["job_category_id"] = filtro.job_category_id
    if filtro.job_type_id:
        filtros["job_type_id"] = filtro.job_type_id
    if filtro.salary_min:
        filtros["salary_min"] = filtro.salary_min
    if filtro.salary_max:
        filtros["salary_max"] = filtro.salary_max
    if filtro.currency_type:
        filtros["currency_type"] = filtro.currency_type
    if filtro.p_english_req is not None:
        filtros["p_english_req"] = filtro.p_english_req
    return filtros


class Command(BaseCommand):
    help = (
        "Busca ofertas para cada FiltroEmpleo activo (configurado en admin) y, "
        "cuando hay ofertas nuevas, envía un resumen por Telegram y por email. "
        "Diseñado para ejecutarse cada hora (cron)."
    )

    def handle(self, *args, **options):
        filtros_activos = FiltroEmpleo.objects.filter(activo=True)
        if not filtros_activos.exists():
            self.stdout.write(
                self.style.WARNING("No hay filtros de empleo activos. Nada que hacer.")
            )
            return

        total_nuevas = 0

        for filtro in filtros_activos:
            filtros = _filtros_desde_modelo(filtro)
            if not filtros.get("search"):
                self.stdout.write(
                    self.style.WARNING(
                        f"Filtro '{filtro.nombre}' sin palabras clave, se omite."
                    )
                )
                continue

            self.stdout.write(
                self.style.WARNING(
                    f"Buscando ofertas para '{filtro.nombre}' ..."
                )
            )

            try:
                ofertas_api = buscar_ofertas_automaticas(
                    filtros, max_pages=filtro.max_pages or 3
                )
            except (ConnectionError, ValueError, RuntimeError) as e:
                self.stderr.write(
                    self.style.ERROR(f"Filtro '{filtro.nombre}': {e}")
                )
                continue
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Filtro '{filtro.nombre}': error inesperado {e}"
                    )
                )
                continue

            _, existentes, resultados = guardar_ofertas(ofertas_api)
            nuevas = [r for r in resultados if r["es_nueva"]]

            self.stdout.write(
                self.style.SUCCESS(
                    f"  {len(ofertas_api)} obtenidas, {len(nuevas)} nuevas, "
                    f"{existentes} ya existentes."
                )
            )

            if not nuevas:
                continue

            total_nuevas += len(nuevas)
            resumen = _resumen_nuevas(nuevas)
            asunto = f"{len(nuevas)} oferta(s) nueva(s): {filtro.nombre}"

            enviado_telegram = enviar_telegram(filtro.telegram_chat_id, f"🔔 {asunto}\n\n{resumen}")
            enviado_email = enviar_email_ofertas(filtro.email_destino, asunto, resumen)

            estado_t, estado_e = "ok" if enviado_telegram else "FALLÓ", "ok" if enviado_email else "FALLÓ"
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Notificaciones para '{filtro.nombre}': "
                    f"Telegram {estado_t} | Email {estado_e}"
                )
            )

        if total_nuevas == 0 and filtros_activos.exists():
            self.stdout.write(
                self.style.SUCCESS("Sin ofertas nuevas. No se enviaron notificaciones.")
            )
