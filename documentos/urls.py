from django.urls import path

from gestor_notas import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.inicio_2, name='inicio'),
    path('inicio_2/', views.inicio_2, name='inicio_2'),
    path('recepcion', views.form_recepcion, name='recepcion'),
    path('load-sub-procedencias/', views.load_sub_procedencias, name='load_sub_procedencias'),
    path('procesamiento', views.form_procesamiento, name='procesamiento'),
    path('aprobacion', views.form_aprobacion, name='aprobacion'),
    path('info_procesada/obtener/<int:id>/', views.obtener_nota_proc, name='obtener_nota_procesada'),
    path('expediente/<int:procesamiento_id>/', views.expediente_json, name='expediente_json'),
    path('expediente_json_procesamiento/<int:procesamiento_id>/', views.expediente_json_procesamiento, name='expediente_json_procesamiento'),
    path('registrar_disposicion/', views.registrar_disposicion, name='registrar_disposicion'),
    path('bandeja/', views.bandeja, name='bandeja'),
    path('actualizar_preregistro_nota/', views.actualizar_nota, name='actualizar_preregistro_nota'),
    path('ver_cumplimiento/<int:cumplimiento_id>/', views.cumplimiento_json, name='ver_cumplimiento'),
    path('registrar_cumplimiento/', views.registrar_cumplimiento, name='registrar_cumplimiento'),
    path('ver_cumplimiento_nota/<int:cumplimiento_id>/', views.cumplimiento_por_nota, name='ver_cumplimiento_nota'),
    path('revisar_recepcion/<int:id>/', views.revisar_recepcion, name='obtener_nota_procesada'),
    path('eliminar_nota/<int:id>/', views.eliminar_nota, name='eliminar_nota'),
    path('revisar_recepcion_arch/<int:procesamiento_id>/', views.revisar_recepcion_arch, name='revisar_recepcion_arch'),
    path('revisar_procesamiento/<int:id>/', views.revisar_procesamiento, name='revisar_procesamiento'),
    path('obtener_disposicion/obtener/<int:id>/', views.obtener_disposicion, name='obtener_disposicion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('nota_destinatarios/<int:id>/', views.nota_destinatarios, name='nota_destinatarios'),
    ]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
