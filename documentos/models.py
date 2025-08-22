import os
from uuid import uuid4
from django.db import models

from django.contrib.auth.models import User
# import pikepdf
from django.core.files.base import ContentFile

MESES_ABREVIADOS_ES = {
        1: 'ENE',
        2: 'FEB',
        3: 'MAR',
        4: 'ABR',
        5: 'MAY',
        6: 'JUN',
        7: 'JUL',
        8: 'AGO',
        9: 'SEP',
        10: 'OCT',
        11: 'NOV',
        12: 'DIC'
        }

def camb_nom_arch(instance, filename):
    return f'nota_{instance.cod_nota.id}/{filename}'
def camb_nom_arch_enviadas(instance, filename):
    return f'nota_enviadas_{instance.id}/{filename}'
def camb_nom_arch_enviadas_resp(instance, filename):
    return f'nota_enviadas_resp_{instance.id}/{filename}'
class usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nom_usuario = models.TextField()
    nombre = models.TextField()
    apellido = models.TextField()
    cod_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mision = models.TextField(null = True)
    vision = models.TextField(null = True)
    def __str__(self):
        fila =  str(self.nom_usuario)
        return fila
    

class procedencia(models.Model):
    id = models.AutoField(primary_key=True)
    descrip_corta = models.TextField()    
    descrip_larga = models.TextField()    
    cod_proced_superior = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategorias')
    color = models.TextField(null = True)
    def __str__(self):
        fila =  str(self.descrip_corta)
        return fila

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    unidad_militar = models.ForeignKey(procedencia, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.usuario.username 
    
class tp_prioridad(models.Model):
    id = models.AutoField(primary_key=True)
    descrip_corta = models.TextField()
    def __str__(self):
        fila = str(self.descrip_corta) 
        return fila


class tp_documentacion(models.Model):
    id = models.AutoField(primary_key=True)
    descrip_corta = models.TextField()
    def __str__(self):
        fila = str(self.descrip_corta) 
        return fila

class tp_medio(models.Model):
    id = models.AutoField(primary_key=True)
    descrip_corta = models.TextField()
    def __str__(self):
        fila = str(self.descrip_corta) 
        return fila

class estado_preregistro(models.Model):
    id = models.AutoField(primary_key=True)
    descrip_corta = models.TextField()
    def __str__(self):
        fila = str(self.descrip_corta) 
        return fila
   
class preregistro_nota(models.Model):
    id = models.AutoField(primary_key=True)
    no_exp = models.TextField()
    fch_rcp = models.DateTimeField(auto_now_add=True)#fecha de recepcion de la nota.
    cod_procedencia = models.ForeignKey(procedencia, on_delete=models.CASCADE)
    cod_medio = models.ForeignKey(tp_medio, on_delete=models.CASCADE,null=True)
    cod_usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cod_estado_preregistro = models.ForeignKey(estado_preregistro, on_delete=models.CASCADE, null = True)
    def formato_fecha(self, fecha):
        if fecha:
            dia = fecha.strftime('%d')
            hora = fecha.strftime('%H%M')
            mes_abrev = MESES_ABREVIADOS_ES[fecha.month]
            año = fecha.strftime('%Y')[1:]  # Últimos 3 dígitos del año
            return f"{dia}{hora}{mes_abrev}{año}"
        return "N/A"

    def fch_rcp_formateada(self):
        return self.formato_fecha(self.fch_rcp)
    class Meta:
        permissions = [
            ("recepcion", "Puede recepcionar y registrar notas"),
            ("procesar", "Puede procesar  notas"),
            ("aprobar", "Puede aprobar notas"),
            ("bandeja", "Puede observar bandeja notas"),
            ]
    
class preregistro_nota_arch(models.Model):
    id = models.AutoField(primary_key=True)
    cod_nota = models.ForeignKey(preregistro_nota, on_delete=models.CASCADE)
    arch = models.FileField(upload_to= camb_nom_arch)
    nombre_archivo = models.CharField(max_length=255, blank=True, null=True)  # Nuevo campo
    def save(self, *args, **kwargs): 
        if self.arch:
            self.nombre_archivo = os.path.basename(self.arch.name) 
            super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # Guardar primero para que exista el archivo en disco
    #     created = self._state.adding  # True si es un nuevo registro
    #     super().save(*args, **kwargs)

    #     if self.arch and self.arch.name.lower().endswith('.pdf'):
    #         try:
    #             pdf_path = self.arch.path
    #             temp_path = pdf_path.replace(".pdf", "_temp.pdf")

    #             with pikepdf.open(pdf_path) as pdf:
    #                 pdf.save(temp_path, linearize=True)

    #             os.replace(temp_path, pdf_path)

    #             # Actualizar nombre_archivo solo si es nuevo o está vacío
    #             if not self.nombre_archivo:
    #                 self.nombre_archivo = os.path.basename(self.arch.name)
    #                 # Guardar solo ese campo sin crear un nuevo registro
    #                 preregistro_nota_arch.objects.filter(id=self.id).update(nombre_archivo=self.nombre_archivo)

    #         except Exception as e:
    #             print(f"⚠️ Error al comprimir PDF: {e}")

class procesamiento_nota(models.Model):
    id = models.AutoField(primary_key=True)
    cod_nota = models.ForeignKey(preregistro_nota, on_delete=models.CASCADE)
    fch_exp = models.DateTimeField()
    fch_limite = models.DateTimeField()
    asunto = models.TextField()#fecha de recepcion de la nota.
    contenido = models.TextField()
    disposicion = models.TextField(null = True)
    cod_usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    tp_prioridad = models.ForeignKey(tp_prioridad, on_delete=models.CASCADE, null = True)
    tp_documentacion = models.ForeignKey(tp_documentacion, on_delete=models.CASCADE, null = True)
    fch_procesamiento = models.DateTimeField(auto_now_add=True)
    
    def formato_fecha(self, fecha):
        if fecha:
            dia = fecha.strftime('%d')
            hora = fecha.strftime('%H%M')
            mes_abrev = MESES_ABREVIADOS_ES[fecha.month]
            año = fecha.strftime('%Y')[1:]  # Últimos 3 dígitos del año
            return f"{dia}{hora}{mes_abrev}{año}"
        return "N/A"

    def fch_exp_formateada(self):
        return self.formato_fecha(self.fch_exp)
      
    def fch_limite_formateada(self):
        return self.formato_fecha(self.fch_limite)
    
    def clase_prioridad(self):
        if self.cod_nota.cod_estado_preregistro.descrip_corta != "Realizada":
            if self.tp_prioridad.id == 1:
                return "prioridad-alta"
            elif self.tp_prioridad.id == 2:
                return "prioridad-media"
            elif self.tp_prioridad.id == 3:
                return "prioridad-baja"
        return ""    
    
    
class estado_cumplimiento(models.Model):
    id = models.AutoField(primary_key=True)
    descrip_corta = models.TextField()
    def __str__(self):
        fila = str(self.descrip_corta) 
        return fila
    
class notaxprocedencia(models.Model):
    id = models.AutoField(primary_key=True)
    cod_nota = models.ForeignKey(procesamiento_nota, on_delete=models.CASCADE)
    cod_procedencia = models.ForeignKey(procedencia, on_delete=models.CASCADE)
    cod_estado_cumplimiento = models.ForeignKey(estado_cumplimiento, on_delete=models.CASCADE,default=1)
    Observacion = models.TextField(null = True)
    
    def clase_prioridad(self):
        if self.cod_estado_cumplimiento.descrip_corta != "Realizada":
            if self.cod_nota.tp_prioridad.id == 1:
                return "prioridad-alta"
            elif self.cod_nota.tp_prioridad.id == 2:
                return "prioridad-media"
            elif self.cod_nota.tp_prioridad.id == 3:
                return "prioridad-baja"
        return ""    

class tp_estado_nota_env(models.Model):
    id = models.AutoField(primary_key=True)
    descrip_corta = models.TextField()
    def __str__(self):
        fila = str(self.descrip_corta) 
        return fila


class notas_enviadas(models.Model):
    id = models.AutoField(primary_key=True)
    fch_env = models.DateField(null=True)
    no_exp = models.TextField(null=True)
    tp_documentacion = models.ForeignKey(tp_documentacion, on_delete=models.CASCADE,default=1)#fecha de recepcion de la nota.
    contenido = models.TextField(null=True)
    procedencia = models.ForeignKey(procedencia, on_delete=models.CASCADE)
    tp_medio = models.ForeignKey(tp_medio, on_delete=models.CASCADE)
    recepcion = models.TextField(null=True)
    completado = models.TextField(null=True)
    tp_estado_nota_env =  models.ForeignKey(tp_estado_nota_env, on_delete=models.CASCADE)
    cod_usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def formato_fecha(self, fecha):
        if fecha:
            dia = fecha.strftime('%d')
            hora = fecha.strftime('%H%M')
            mes_abrev = MESES_ABREVIADOS_ES[fecha.month]
            año = fecha.strftime('%Y')[1:]  # Últimos 3 dígitos del año
            return f"{dia}{mes_abrev}{año}"
        return "N/A"

    def fch_env_formateada(self):
        return self.formato_fecha(self.fch_env)
    
    def clase_prioridad(self):
        if self.tp_estado_nota_env.descrip_corta != "Completada":
            if self.tp_estado_nota_env.id == 1:
                return "prioridad-alta"
        return ""   
    class Meta:
        permissions = [
            ("registra_notas_enviadas", "Puede gestionar las notas enviadas"),
            ]    
        
class nota_env_arch(models.Model):
    id = models.AutoField(primary_key=True)
    cod_nota_enviada = models.ForeignKey(notas_enviadas, on_delete=models.CASCADE)
    arch = models.FileField(upload_to= camb_nom_arch_enviadas)
    nombre_archivo = models.CharField(max_length=255, blank=True, null=True)  # Nuevo campo
    def save(self, *args, **kwargs): 
        if self.arch:
            self.nombre_archivo = os.path.basename(self.arch.name) 
            super().save(*args, **kwargs)

class nota_env_resp_arch(models.Model):
    id = models.AutoField(primary_key=True)
    cod_nota_enviada = models.ForeignKey(notas_enviadas, on_delete=models.CASCADE)
    arch = models.FileField(upload_to= camb_nom_arch_enviadas_resp)
    nombre_archivo = models.CharField(max_length=255, blank=True, null=True)  # Nuevo campo
    def save(self, *args, **kwargs): 
        if self.arch:
            self.nombre_archivo = os.path.basename(self.arch.name) 
            super().save(*args, **kwargs)
            
class evidencia_cumpli_nota_arch(models.Model):
    id = models.AutoField(primary_key=True)
    cod_nota = models.ForeignKey(notaxprocedencia, on_delete=models.CASCADE)
    arch = models.FileField(upload_to= camb_nom_arch)
    nombre_archivo = models.CharField(max_length=255, blank=True, null=True)  # Nuevo campo
    
    def save(self, *args, **kwargs): 
        if self.arch:
            self.nombre_archivo = os.path.basename(self.arch.name) 
            super().save(*args, **kwargs)
    # def save(self, *args, **kwargs):
    #     # Guardar primero para que exista el archivo en disco
    #     created = self._state.adding  # True si es un nuevo registro
    #     super().save(*args, **kwargs)

    #     if self.arch and self.arch.name.lower().endswith('.pdf'):
    #         try:
    #             pdf_path = self.arch.path
    #             temp_path = pdf_path.replace(".pdf", "_temp.pdf")

    #             with pikepdf.open(pdf_path) as pdf:
    #                 pdf.save(temp_path, linearize=True)

    #             os.replace(temp_path, pdf_path)

    #             # Actualizar nombre_archivo solo si es nuevo o está vacío
    #             if not self.nombre_archivo:
    #                 self.nombre_archivo = os.path.basename(self.arch.name)
    #                 # Guardar solo ese campo sin crear un nuevo registro
    #                 preregistro_nota_arch.objects.filter(id=self.id).update(nombre_archivo=self.nombre_archivo)

    #         except Exception as e:
    #             print(f"⚠️ Error al comprimir PDF: {e}")
    
class nota_disp_arch(models.Model):
    id = models.AutoField(primary_key=True)
    cod_nota = models.ForeignKey(procesamiento_nota, on_delete=models.CASCADE)
    arch = models.FileField(upload_to= camb_nom_arch_enviadas)
    nombre_archivo = models.CharField(max_length=255, blank=True, null=True)  # Nuevo campo
    def save(self, *args, **kwargs): 
        if self.arch:
            self.nombre_archivo = os.path.basename(self.arch.name) 
            super().save(*args, **kwargs)
