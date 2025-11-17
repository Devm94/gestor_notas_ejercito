import json
from pyexpat.errors import messages
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
import pandas as pd
from .models import *
from django.utils.timezone import make_aware
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io
import openpyxl
from django.http import FileResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils.dateparse import parse_date

from django.contrib.auth import logout


@login_required
def inicio(request):
    return render(request, 'index.html')
@login_required
def inicio_2(request):
    log_user = usuario.objects.get(cod_user=request.user)
    nom_completo = log_user.cod_user.first_name + " " + log_user.cod_user.last_name
    totalnotas = preregistro_nota.objects.count()
    totalnotas_completados = preregistro_nota.objects.filter(cod_estado_preregistro = estado_preregistro.objects.get(id = 7)).count()
    totalnotas_pendientes = preregistro_nota.objects.exclude(cod_estado_preregistro = estado_preregistro.objects.get(id = 7)).count()

    context = {
        'CV': f"{totalnotas:,}",
        'ME' : f"{totalnotas_completados:,}",
        'RH' : f"{totalnotas_pendientes:,}",
        'Mision' : log_user.mision,
        'Vision' : log_user.vision,
        'nom_completo' : nom_completo,

    }
    return render(request, 'core/base.html', context)
@login_required
def load_sub_procedencias(request):
    procedencia_id = request.GET.get('procedencia_id')  # Obtener la ID de la marca desde la solicitud Ajax
    sub_procedencia = procedencia.objects.filter(cod_proced_superior=procedencia_id).order_by('descrip_corta')  # Filtrar modelos por marca
    return JsonResponse(list(sub_procedencia.values('id', 'descrip_corta')), safe=False)
@login_required
def form_recepcion(request):
    ls_procedencia = procedencia.objects.filter(cod_proced_superior__isnull=True)
    ls_preregistro_notas = preregistro_nota.objects.order_by('-fch_rcp').all()
    medio = tp_medio.objects.all()
    context = {'ls_procedencia' : ls_procedencia ,
               'ls_preregistro_notas' : ls_preregistro_notas,
               'tp_medio' : medio}
    if request.method == "POST":
        preregistro_c = preregistro_nota.objects.create(
            no_exp = request.POST['numExpediente'],
            cod_procedencia = procedencia.objects.get(id=request.POST['sub_procedencia']),
            cod_usuario = User.objects.get(username=request.user),
            cod_estado_preregistro = estado_preregistro.objects.get(id=1),
            cod_medio = tp_medio.objects.get(id=request.POST['medio'])
        ) 

        for file in request.FILES.getlist('arch'):
            preregistro_nota_arch.objects.create(
                cod_nota=preregistro_c,
                arch=file
            )
        return redirect('recepcion')
    else:
        return render(request, 'documentacion/form_recepcion.html', context)
@login_required
def form_procesamiento(request):
    ls_tp_prioridad = tp_prioridad.objects.all()
    ls_preregistro_notas = preregistro_nota.objects.order_by("cod_estado_preregistro").all()
    v_tp_documentacion = tp_documentacion.objects.all()
    ls_procedencia = procedencia.objects.filter(cod_proced_superior__isnull=True)
    context = {'ls_preregistro_notas' : ls_preregistro_notas,
               'ls_tp_prioridad' : ls_tp_prioridad,
               'v_tp_documentacion' : v_tp_documentacion,
               'ls_procedencia' : ls_procedencia ,}
    if request.method == "POST":
        print("Registrada")
        fch_nota_c = datetime.strptime(request.POST['fch_exp'], "%Y-%m-%dT%H:%M")
        fch_nota_c = make_aware(fch_nota_c)
        fch_limite_c = datetime.strptime(request.POST['fch_limite'], "%Y-%m-%dT%H:%M")
        fch_limite_c = make_aware(fch_limite_c)
        procesamiento_nota.objects.create(
            cod_nota = preregistro_nota.objects.get(id=request.POST['itemId']),
            fch_exp = fch_nota_c,
            fch_limite = fch_limite_c,
            tp_documentacion = tp_documentacion.objects.get(id=request.POST['tp_documentacion']),
            contenido = request.POST['contenido'],
            tp_prioridad = tp_prioridad.objects.get(id=request.POST['tp_prioridad']),
            cod_usuario = User.objects.get(username=request.user),
            )
        nuevo_estado = estado_preregistro.objects.get(id=2)  # Ejemplo: ID del nuevo estado
        preregistro_nota.objects.filter(id=request.POST['itemId']).update(cod_estado_preregistro=nuevo_estado)
        return redirect('procesamiento')
    else:
        return render(request, 'documentacion/form_procesamiento.html', context)
@login_required    
def form_aprobacion(request):
    ls_procedencia = procedencia.objects.filter(cod_proced_superior__isnull=True)
    notas = procesamiento_nota.objects.order_by('-cod_nota__cod_estado_preregistro', 'tp_prioridad').all()
    context = {
        'ls_procedencia' : ls_procedencia ,
        'notas_procesadas' : notas,
    }

    return render(request, 'documentacion/form_aprobacion.html', context)
@login_required
def obtener_nota_proc(request, id):
    nota_proces = procesamiento_nota.objects.get(pk=id)
    fch_limite = nota_proces.fch_limite_formateada()
    fch_exp = nota_proces.fch_exp_formateada()
    
    data = {
        'id': nota_proces.id,
        'fch_exp': fch_exp ,
        'fch_limite': fch_limite,
        'tp_prioridad': nota_proces.tp_prioridad.descrip_corta,
        'asunto': nota_proces.asunto ,
        'contenido': nota_proces.contenido ,
        'procedencia': nota_proces.cod_nota.cod_procedencia.descrip_corta,
        'disposicion': nota_proces.disposicion,
    }
    return JsonResponse(data)
@login_required
def revisar_recepcion(request, id):
    nota_proces = preregistro_nota.objects.get(pk=id)
    print(nota_proces.cod_procedencia.cod_proced_superior)
    data = {
        'id': id,
        'medio': nota_proces.cod_medio.descrip_corta,
        'num_exp': nota_proces.no_exp,
        'procedencia': str(nota_proces.cod_procedencia),
        'procedencia_sup': str(nota_proces.cod_procedencia.cod_proced_superior),
        'c_medio': nota_proces.cod_medio.id,
        'c_procedencia': nota_proces.cod_procedencia.id,
        'c_procedencia_sup': nota_proces.cod_procedencia.cod_proced_superior.id,
        }
    return JsonResponse(data)
@login_required
def revisar_procesamiento(request, id):
    nota_proces = procesamiento_nota.objects.get(cod_nota=preregistro_nota.objects.get(id = id))
    fch_limite = nota_proces.fch_limite_formateada()
    fch_exp = nota_proces.fch_exp_formateada()
    
    data = {
        'id': nota_proces.id,
        'fch_exp': fch_exp ,
        'fch_limite': fch_limite,
        'tp_prioridad': nota_proces.tp_prioridad.descrip_corta,
        'tp_documentacion': nota_proces.tp_documentacion.descrip_corta ,
        'contenido': nota_proces.contenido ,
        'procedencia': nota_proces.cod_nota.cod_procedencia.descrip_corta,
        'disposicion': nota_proces.disposicion,
    }
    return JsonResponse(data)
@login_required
def expediente_json(request, procesamiento_id):
    procesamiento = procesamiento_nota.objects.get(id=procesamiento_id)
    archivos = preregistro_nota_arch.objects.filter(cod_nota=procesamiento.cod_nota)

    data = {
        "archivos": [
            {"nombre": a.nombre_archivo, "url": a.arch.url}
            for a in archivos
        ]
    }
    return JsonResponse(data)

@login_required
def revisar_recepcion_arch(request, procesamiento_id):
    print(procesamiento_id)
    procesamiento = preregistro_nota.objects.get(id=procesamiento_id)
    archivos = preregistro_nota_arch.objects.filter(cod_nota=procesamiento)

    data = {
        "archivos": [
            {"nombre": a.nombre_archivo, "url": a.arch.url}
            for a in archivos
        ]
    }
    return JsonResponse(data)
def expediente_json_procesamiento(request, procesamiento_id):
    procesamiento = preregistro_nota.objects.get(id=procesamiento_id)
    
    archivos = preregistro_nota_arch.objects.filter(cod_nota=procesamiento)
    print(archivos)
    data = {
        "archivos": [
            {"nombre": a.nombre_archivo, "url": a.arch.url}
            for a in archivos
        ]
        
    }
    print(data)
    return JsonResponse(data)
@login_required
@csrf_exempt
def registrar_disposicion(request):
    if request.method == 'POST':
        try:
            
            item_id = request.POST.get('itemIdx')
            contenido = request.POST.get('contenido') or request.POST.get('disposicion')
            destinatarios_json = request.POST.get('destinatarios')
            proc = procesamiento_nota.objects.get(cod_nota__id=item_id)
            proc.disposicion = contenido
            print(destinatarios_json)
            nota_preregistro = preregistro_nota.objects.get(id = proc.cod_nota.id)
            nota_preregistro.cod_estado_preregistro = estado_preregistro.objects.get(id = 8)
            nota_preregistro.save()
            proc.save()
            
            for file in request.FILES.getlist('arch_notas_enviadas'):
                nota_disp_arch.objects.create(
                    cod_nota=proc,
                    arch=file
                )
            
            if destinatarios_json:
                
                destinatarios = json.loads(destinatarios_json)
                for dest in destinatarios:
                    sub_procedencia_id = dest.get('sub_procedencia')
                    if sub_procedencia_id != None:
                        print(sub_procedencia_id)
                        notaxprocedencia.objects.create(
                            cod_nota=proc,
                            cod_procedencia=procedencia.objects.get(id=sub_procedencia_id)
                            )
            return JsonResponse({'status': 'ok', 'message': 'Disposición y destinatarios registrados correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def bandeja(request):
    
    if request.user.is_superuser:
        notas = notaxprocedencia.objects.all().order_by('cod_estado_cumplimiento')
    else:
        perfil = PerfilUsuario.objects.get(usuario=request.user)
        print(perfil)
        id_procedencia = perfil.unidad_militar.pk
        print(id_procedencia)
        procedencia_padre = procedencia.objects.get(id=id_procedencia)
        todos_los_ids = obtener_subprocedencias(procedencia_padre)
        print(todos_los_ids)
        notas = notaxprocedencia.objects.filter(cod_procedencia__in=todos_los_ids).order_by('cod_estado_cumplimiento') # Incluir la procedencia principal
    context = {
        'notas': notas,
    }
    return render(request, 'documentacion/bandeja.html', context)
    
@csrf_exempt
@login_required
def registrar_cumplimiento(request):
    if request.method == 'POST':
        try:
            
            item_id = request.POST.get('itemIdx')
            cumplimiento = request.POST.get('cumplimiento')
            proc = notaxprocedencia.objects.get(id=item_id)
            proc.Observacion = cumplimiento
            proc.cod_estado_cumplimiento = estado_cumplimiento.objects.get(id=2)
            for file in request.FILES.getlist('arch'):
                evidencia_cumpli_nota_arch.objects.create(
                cod_nota=notaxprocedencia.objects.get(id=item_id),
                arch=file
            )
            proc.save()
            nota = proc.cod_nota  # Relación hacia preregistro_nota
            pendientes = notaxprocedencia.objects.filter(cod_nota=nota).exclude(cod_estado_cumplimiento__id=2).exists()
            print(pendientes)
            if not pendientes:
                print("entro")
                completado = preregistro_nota.objects.get(id = nota.cod_nota.id)
                completado.cod_estado_preregistro = estado_preregistro.objects.get(id=7)  # Ejemplo: 9 = "Cumplido"
                print(nota)
                completado.save()  
            return JsonResponse({'status': 'ok', 'message': 'Disposición y destinatarios registrados correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def cumplimiento_json(request, cumplimiento_id):
    print(cumplimiento_id)
    procesamiento = notaxprocedencia.objects.get(id=cumplimiento_id)
    archivos = evidencia_cumpli_nota_arch.objects.filter(cod_nota=procesamiento)
    cumplimiento =  procesamiento.Observacion
    print(archivos)
    print(cumplimiento)
    data = {
        "archivos": [
            {"nombre": a.nombre_archivo, "url": a.arch.url}
            for a in archivos
        ],
        'cumplimiento' : cumplimiento, 
    }
    return JsonResponse(data)
def cerrar_sesion(request):
    logout(request)
    return redirect(inicio_2) 

def obtener_subprocedencias(procedencia):
    subcategorias = procedencia.subcategorias.all()
    if not subcategorias:
        return {procedencia.id}  # solo el padre si no hay hijos

    subprocedencias = set()
    for sub in subcategorias:
        subprocedencias.add(sub.id)
        subprocedencias.update(obtener_subprocedencias(sub))
    return subprocedencias

def cumplimiento_por_nota(request, cumplimiento_id):
    # Filtramos las procedencias de la nota
    print(cumplimiento_id)
    procedencias = notaxprocedencia.objects.filter(cod_nota__id=cumplimiento_id)
    
    data = []
    for proc in procedencias:
        # Obtenemos las evidencias de cumplimiento asociadas a esa procedencia
        evidencias = evidencia_cumpli_nota_arch.objects.filter(cod_nota=proc)
        evidencias_data = [
            {
                "id": ev.id,
                "nombre": ev.nombre_archivo,
                "archivo": ev.arch.url if ev.arch else None,
            }
            for ev in evidencias
        ]

        data.append({
            "id": proc.id,
            "procedencia": proc.cod_procedencia.nombre if hasattr(proc.cod_procedencia, "nombre") else str(proc.cod_procedencia),
            "estado_cumplimiento": proc.cod_estado_cumplimiento.descrip_corta,
            "observacion": proc.Observacion,
            "clase_prioridad": proc.clase_prioridad(),
            "documentos": evidencias_data,
        })

    return JsonResponse(data, safe=False)

def cumplimiento_por_nota_proc(request, cumplimiento_id):
    nota = procesamiento_nota.objects.get(cod_nota__id = cumplimiento_id)
    print(nota.id)
    procedencias = notaxprocedencia.objects.filter(cod_nota__id=nota.id)

    data = []
    for proc in procedencias:
        # Obtenemos las evidencias de cumplimiento asociadas a esa procedencia
        evidencias = evidencia_cumpli_nota_arch.objects.filter(cod_nota=proc)
        
        evidencias_data = [
            {
                "id": ev.id,
                "nombre": ev.nombre_archivo,
                "archivo": ev.arch.url if ev.arch else None,
            }
            for ev in evidencias
        ]

        data.append({
            "id": proc.id,
            "procedencia": proc.cod_procedencia.nombre if hasattr(proc.cod_procedencia, "nombre") else str(proc.cod_procedencia),
            "estado_cumplimiento": proc.cod_estado_cumplimiento.descrip_corta,
            "observacion": proc.Observacion,
            "clase_prioridad": proc.clase_prioridad(),
            "documentos": evidencias_data,
        })

    return JsonResponse(data, safe=False)

@csrf_exempt  # si usas fetch, asegúrate de mandar el CSRF en headers
def actualizar_nota(request):
    if request.method == "POST":
        nota_id = request.POST.get("id_nota_c")
        nota_exp = request.POST.get("c_numExpediente")
        medio_id = request.POST.get("c_medio")
        sub_procedencia_id = request.POST.get("c_sub_procedencia")

        try:
            nota = preregistro_nota.objects.get(id=nota_id)
            nota.medio_id = medio_id
            nota.no_exp = nota_exp
            nota.cod_procedencia = procedencia.objects.get(id=sub_procedencia_id)
            nota.cod_estado_preregistro = estado_preregistro.objects.get(id=5)
            nota.save()

            return JsonResponse({
                "success": True,
                "nota_id": nota.id,
                "estado": nota.no_exp,
                "procedencia": nota.cod_procedencia.descrip_corta,
            })
        except preregistro_nota.DoesNotExist:
            return JsonResponse({"success": False, "error": "Nota no encontrada"})
    
    return JsonResponse({"success": False, "error": "Método no permitido"})

def eliminar_nota(request, id):
    nota = get_object_or_404(preregistro_nota, id=id)
    nota.delete()
    return redirect('recepcion')  # Cambia por la URL de tu lista

@login_required
def obtener_disposicion(request, id, otro_id):
    if otro_id == 2:
        id =  procesamiento_nota.objects.get(cod_nota__id = id)
        id = id.id

        
    nota_proces = procesamiento_nota.objects.get(pk=id)

    data = {
        'id': nota_proces.id,
        'disposicion': nota_proces.disposicion or "",
    }
    return JsonResponse(data)

def nota_destinatarios(request, id):
    try:
        nota = procesamiento_nota.objects.get(id=id)
    except procesamiento_nota.DoesNotExist:
        return JsonResponse({"error": "Nota no encontrada"}, status=404)

    # Obtener destinatarios relacionados
    destinatarios = notaxprocedencia.objects.filter(cod_nota=nota)

    destinatarios_data = []
    for d in destinatarios:
        destinatarios_data.append({
            "id": d.id,
            "procedencia_id": d.cod_procedencia.id,
            "procedencia_nombre": d.cod_procedencia.descrip_corta,
            "observacion": d.Observacion or ""
        })

    return JsonResponse({"nota_id": nota.id, "destinatarios": destinatarios_data})

def imprimir_nota(request, pk):
    print(pk)
    nota = procesamiento_nota.objects.get(id=pk)
    print(nota)
    return render(request, "documentacion/disposicion_print.html", {"nota": nota})
def imprimir_nota_proc(request, pk):
    nota = procesamiento_nota.objects.get(cod_nota=pk)
    return render(request, "documentacion/disposicion_print.html", {"nota": nota})

@login_required
def nota_enviada(request):
    v_notas_enviadas = notas_enviadas.objects.exclude(tp_estado_nota_env = tp_estado_nota_env.objects.get(id = 3)).order_by('tp_estado_nota_env', '-fch_env').all()
    v_procedencia = procedencia.objects.filter(cod_proced_superior__isnull=True)
    v_tp_documentacion = tp_documentacion.objects.all()
    v_tp_medio = tp_medio.objects.all()
    v_tp_estado_nota_env = tp_estado_nota_env.objects.all()
    context = {
        'v_notas_enviadas' : v_notas_enviadas,
        'v_procedencia' : v_procedencia,
        'v_tp_documentacion' : v_tp_documentacion,
        'v_tp_medio' : v_tp_medio,
        'v_tp_estado_nota_env' : v_tp_estado_nota_env,
        }
    if request.method == "POST":
        if request.POST['itemId'] == "":            
            r_notas_enviadas = notas_enviadas.objects.create(
                fch_env = request.POST['fch_env'],
                no_exp = request.POST['numExpediente'],
                tp_documentacion = tp_documentacion.objects.get(id=request.POST['tp_documentacion']),
                contenido = request.POST['contenido'],
                procedencia = procedencia.objects.get(id=request.POST['sub_procedencia']),
                tp_medio = tp_medio.objects.get(id=request.POST['tp_medio']),
                tp_estado_nota_env = tp_estado_nota_env.objects.get(id=1,),
                cod_usuario = User.objects.get(username=request.user),) 
            for file in request.FILES.getlist('arch_notas_enviadas'):
                nota_env_arch.objects.create(
                    cod_nota_enviada=r_notas_enviadas,
                    arch=file
                )
        else:
            v_nota_enviada = notas_enviadas.objects.get(pk=request.POST['itemId'])
            v_nota_enviada.fch_env = request.POST['fch_env']
            v_nota_enviada.no_exp = request.POST['numExpediente']
            v_nota_enviada.tp_documentacion = tp_documentacion.objects.get(id=request.POST['tp_documentacion'])
            v_nota_enviada.contenido = request.POST['contenido']
            v_nota_enviada.tp_medio = tp_medio.objects.get(id=request.POST['tp_medio'])
            v_nota_enviada.cod_usuario = User.objects.get(username=request.user)
            v_nota_enviada.save()
            for file in request.FILES.getlist('arch_notas_enviadas'):
                nota_env_arch.objects.create(cod_nota_enviada=v_nota_enviada,arch=file)
        return redirect('notas_enviadas')
    else:
        return render(request, 'documentacion/notas_enviadas.html', context)
    

@csrf_exempt
@login_required
def registrar_completado(request):
    if request.method == 'POST':
        try:
            print("Furula")
            item_id = request.POST.get('id_nota_enviada')
            completado = request.POST.get('completado')
            proc = notas_enviadas.objects.get(id=item_id)
            proc.completado = completado
            proc.tp_estado_nota_env = tp_estado_nota_env.objects.get(id=2)
            
            for file in request.FILES.getlist('fileInput1'):
                nota_env_resp_arch.objects.create(
                cod_nota_enviada=proc,
                arch=file
            )
            proc.save()
            return JsonResponse({'status': 'ok', 'message': 'Disposición y destinatarios registrados correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def ver_completado(request, cumplimiento_id):
    v_notas_enviadas = notas_enviadas.objects.get(id=cumplimiento_id)
    archivos = nota_env_resp_arch.objects.filter(cod_nota_enviada=v_notas_enviadas)
    completado =  v_notas_enviadas.completado
    data = {
        "archivos": [
            {"nombre": a.nombre_archivo, "url": a.arch.url}
            for a in archivos
        ],
        'completado' : completado, 
    }
    return JsonResponse(data)

@login_required
def revisar_envio_arch(request, envio_nota_id):
    v_nota_enviada = notas_enviadas.objects.get(id=envio_nota_id)
    archivos = nota_env_arch.objects.filter(cod_nota_enviada=v_nota_enviada)

    data = {
        "archivos": [
            {"nombre": a.nombre_archivo, "url": a.arch.url}
            for a in archivos
        ]
    }
    print(data)
    return JsonResponse(data)

def revisar_nota_enviada(request, id):
    v_nota_enviada = notas_enviadas.objects.get(pk=id)
    data = {
        'id': id,
        'fch_env': v_nota_enviada.fch_env,
        'num_exp': v_nota_enviada.no_exp,
        'tp_documentacion':str(v_nota_enviada.tp_documentacion.id),
        'tp_medio': str(v_nota_enviada.tp_medio.id),
        'contenido': v_nota_enviada.contenido,
        'procedencia': str(v_nota_enviada.procedencia.id),
        'procedencia_sup': str(v_nota_enviada.procedencia.cod_proced_superior.id),
        }
    return JsonResponse(data)

@login_required
def revisar_envio_resp_arch(request, envio_resp_nota_id):
    v_nota_enviada = notas_enviadas.objects.get(id=envio_resp_nota_id)
    archivos = nota_env_resp_arch.objects.filter(cod_nota_enviada=v_nota_enviada)

    data = {
        "archivos": [
            {"nombre": a.nombre_archivo, "url": a.arch.url}
            for a in archivos
        ]
    }
    print(data)
    return JsonResponse(data)

def eliminar_nota_enviada(request, id):
    nota_enviada = notas_enviadas.objects.get(id=id)
    nota_enviada.tp_estado_nota_env = tp_estado_nota_env.objects.get(id = 3)
    nota_enviada.cod_usuario = User.objects.get(username=request.user)
    nota_enviada.save()
    return redirect('notas_enviadas') 

@login_required
def revisar_disp_arch(request, envio_nota_id):
    v_disp_nota = procesamiento_nota.objects.get(id=envio_nota_id)
    archivos = nota_disp_arch.objects.filter(cod_nota=v_disp_nota)
    data = {
        "archivos": [
            {"nombre": a.nombre_archivo, "url": a.arch.url}
            for a in archivos
        ]
    }
    return JsonResponse(data)

def api_eventos(request):
    eventos = []
    notas = procesamiento_nota.objects.all()
    for nota in notas:
        eventos.append({
            "id": nota.id,
            "title": nota.tp_documentacion.descrip_corta + "-" + str(nota.cod_nota.cod_procedencia),  # el asunto será el texto que se muestra
            "tipo_doc": nota.tp_documentacion.descrip_corta,
            "asunto": nota.tp_documentacion.descrip_corta,
            "start": nota.fch_limite.strftime("%Y-%m-%dT%H:%M:%S"),  # fecha límite
            "end": nota.fch_limite.strftime("%Y-%m-%dT%H:%M:%S"),
            "backgroundColor":nota.cod_nota.cod_procedencia.cod_proced_superior.color,  # color opcional
            "borderColor": nota.cod_nota.cod_procedencia.cod_proced_superior.color,
            "allDay": False,
            "procedencia": nota.cod_nota.cod_procedencia.descrip_larga,
            "contenido": nota.contenido,
            "disposicion": nota.disposicion,
        })
    return JsonResponse(eventos, safe=False)

def calendario(request):
    return render(request, "documentacion/calendario.html")

def reporte_mensual(request):
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    notas = None  # No mostrar nada por defecto

    # Solo filtrar si el usuario envió ambos campos de fecha
    if fecha_desde and fecha_hasta:
        try:
            desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
            hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            notas = procesamiento_nota.objects.filter(fch_exp__range=[desde, hasta])
        except ValueError:
            notas = None  # Si las fechas no son válidas, no mostrar nada

    context = {
        'notas': notas,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    return render(request, 'documentacion/reportes/mensual.html', context)

def exportar_pdf(request):
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    notas = procesamiento_nota.objects.all()

    if desde and hasta:
        notas = notas.filter(fch_exp__date__range=[desde, hasta])

    template_path = 'reporte_pdf.html'  # crea esta plantilla (puede ser simple)
    context = {'notas': notas, 'desde': desde, 'hasta': hasta}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_notas.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa.CreatePDF(html, dest=response)
    return response

def exportar_excel(request):
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    notas = procesamiento_nota.objects.all()

    if desde and hasta:
        notas = notas.filter(fch_exp__date__range=[desde, hasta])

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Notas'

    # Encabezados
    headers = ['No.', 'Fecha', 'Registro', 'Procedencia', 'Contenido', 'Disposición', 'Observación']
    sheet.append(headers)

    for i, nota in enumerate(notas, start=1):
        sheet.append([
            i,
            nota.fch_exp.strftime('%Y-%m-%d'),
            nota.cod_nota.no_exp,
            nota.cod_nota.cod_procedencia.descrip_larga,
            nota.contenido,
            nota.disposicion,
            nota.cod_estado_cumplimiento if hasattr(nota, 'cod_estado_cumplimiento') else ''
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_notas.xlsx"'
    workbook.save(response)
    return response

def actualizar_estado_nota(request):
    print("hola")
    if request.method == "POST":
        print("hola2")
        nota_id_2 = request.POST.get('nota_id_2')
        print(nota_id_2)
        nota = preregistro_nota.objects.get(id=nota_id_2)
        print(nota)
        estado_cumplido = estado_preregistro.objects.get(id=7)
        nota.cod_estado_preregistro = estado_cumplido
        nota.save()
        estado_realizada = estado_cumplimiento.objects.get(id=2)
        relacionados = notaxprocedencia.objects.filter(cod_nota__cod_nota=nota)
        for r in relacionados:
            r.cod_estado_cumplimiento = estado_realizada
            r.save()
        return redirect(form_procesamiento)