from datetime import date
from documentos.models import estado_preregistro, preregistro_nota, usuario, procesamiento_nota


def notificaciones_usuario(request):
    if request.user.is_authenticated:
        log_user = usuario.objects.get(cod_user=request.user)
        nom_completo = log_user.cod_user.first_name + " " + log_user.cod_user.last_name
        totalnotas = preregistro_nota.objects.count()
        totalnotas_completados = preregistro_nota.objects.filter(cod_estado_preregistro = estado_preregistro.objects.get(id = 7)).count()
        hoy = date.today()
        totalnotas_pendientes = preregistro_nota.objects.exclude(cod_estado_preregistro = estado_preregistro.objects.get(id = 7)).count()
        notificaciones = procesamiento_nota.objects.exclude(cod_nota__cod_estado_preregistro = estado_preregistro.objects.get(id = 7)).filter(fch_limite__date__lte=hoy)
        noti_count = procesamiento_nota.objects.exclude(cod_nota__cod_estado_preregistro = estado_preregistro.objects.get(id = 7)).filter(fch_limite__date__lte=hoy).count() | 0
    else:
        totalnotas_pendientes = None
        notificaciones = notificaciones = preregistro_nota.objects.exclude(cod_estado_preregistro = estado_preregistro.objects.get(id = 7))
        noti_count = f"{totalnotas_pendientes:,}" if totalnotas_pendientes else "0"
        log_user = None
    return {
        'notificaciones': notificaciones,
        'noti_count': noti_count,
        'usuario' : log_user,
    }


