from django.db import models

class Cobertura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Paciente(models.Model):
    nombre = models.CharField(max_length=200)
    dni = models.CharField(max_length=20, blank=True)
    cobertura = models.ForeignKey(Cobertura, on_delete=models.SET_NULL, null=True, blank=True)
    nro_afiliado = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.dni})"

class Internacion(models.Model):
    ESTADOS = [
        ("autorizado", "Autorizado"),
        ("pendiente", "Pendiente"),
        ("solicitado", "Solicitado"),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="internaciones")
    sector = models.CharField(max_length=100, blank=True)
    diagnostico = models.CharField(max_length=255, blank=True)
    fecha_ingreso = models.DateField()
    fecha_egreso = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    prorroga_estado = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"Internación {self.id} - {self.paciente}"

def hc_upload_to(instance, filename):
    return f"internaciones/hc/{instance.paciente_id}/{instance.tab}/{filename}"

class HCDocument(models.Model):
    TABS = [
        ("autorizaciones", "Autorizaciones y Prórrogas"),
        ("epicrisis", "Epicrisis"),
        ("boletin", "Boletín Operatorio / Parte Anestésico"),
        ("evol_med", "Evolución Médica"),
        ("evol_enf", "Evolución de Enfermería"),
        ("interconsultas", "Interconsultas"),
        ("laboratorio", "Laboratorio"),
        ("imagenes", "Imágenes"),
        ("otros", "Otros documentos"),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="documentos")
    tab = models.CharField(max_length=30, choices=TABS)
    archivo = models.FileField(upload_to=hc_upload_to)
    nombre_visible = models.CharField(max_length=255)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.paciente} - {self.get_tab_display()} - {self.nombre_visible}"
