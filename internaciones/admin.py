from django.contrib import admin
from .models import Cobertura, Paciente, Internacion, HCDocument

admin.site.register(Cobertura)
admin.site.register(Paciente)
admin.site.register(Internacion)
admin.site.register(HCDocument)
