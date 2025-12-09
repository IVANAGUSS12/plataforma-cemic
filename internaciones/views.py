from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils.timezone import now

from .models import Paciente, Internacion, HCDocument, Cobertura
from .forms import HCDocumentForm

def _estado_color(estado: str) -> str:
    estado = (estado or "").lower()
    if "autoriz" in estado:
        return "success"
    if "pend" in estado:
        return "warning"
    if "solicit" in estado:
        return "info"
    return "info"

def _prorroga_color(p: str) -> str:
    p = (p or "").lower()
    if "vencid" in p:
        return "danger"
    if "por pedir" in p or ">10" in p:
        return "warning"
    if "vigent" in p:
        return "success"
    return "info"

def censo(request):
    qs = Internacion.objects.select_related("paciente", "paciente__cobertura").all()

    texto = request.GET.get("search") or ""
    if texto:
        qs = qs.filter(
            Q(paciente__nombre__icontains=texto)
            | Q(paciente__dni__icontains=texto)
            | Q(paciente__nro_afiliado__icontains=texto)
        )

    estado = request.GET.get("estado") or ""
    if estado:
        qs = qs.filter(estado=estado.lower())

    cobertura = request.GET.get("cobertura") or ""
    if cobertura:
        qs = qs.filter(paciente__cobertura__nombre__iexact=cobertura)

    sector = request.GET.get("sector") or ""
    if sector:
        qs = qs.filter(sector__icontains=sector)

    orden = request.GET.get("orden") or ""
    if orden == "fecha_ingreso":
        qs = qs.order_by("-fecha_ingreso")
    elif orden == "apellido":
        qs = qs.order_by("paciente__nombre")

    internaciones = []
    for i in qs:
        internaciones.append(
            {
                "id": i.id,
                "sector": i.sector,
                "nombre": i.paciente.nombre,
                "dni": i.paciente.dni,
                "cobertura": i.paciente.cobertura.nombre if i.paciente.cobertura else "",
                "diagnostico": i.diagnostico,
                "afiliado": i.paciente.nro_afiliado,
                "fecha_ingreso": i.fecha_ingreso,
                "fecha_egreso": i.fecha_egreso,
                "estado": i.get_estado_display(),
                "estado_color": _estado_color(i.get_estado_display()),
                "prorroga_estado": i.prorroga_estado or "",
                "prorroga_color": _prorroga_color(i.prorroga_estado or ""),
            }
        )

    coberturas = Cobertura.objects.all()

    contexto = {
        "internaciones": internaciones,
        "coberturas": coberturas,
    }
    return render(request, "internaciones/censo_lista.html", contexto)

def ver_internacion(request, pk):
    internacion = get_object_or_404(
        Internacion.objects.select_related("paciente", "paciente__cobertura"), pk=pk
    )
    paciente = internacion.paciente

    contexto = {
        "internacion": internacion,
        "paciente": paciente,
        "estado_color": _estado_color(internacion.get_estado_display()),
    }
    return render(request, "internaciones/censo_ver_internacion.html", contexto)

def censo_cobertura(request, cobertura_nombre):
    cobertura = get_object_or_404(Cobertura, nombre__iexact=cobertura_nombre)
    hoy = now().date()
    qs = Internacion.objects.filter(
        paciente__cobertura=cobertura,
        fecha_ingreso__lte=hoy
    ).filter(
        Q(fecha_egreso__isnull=True) | Q(fecha_egreso__gte=hoy)
    ).select_related("paciente")

    internaciones = []
    for i in qs:
        internaciones.append(
            {
                "id": i.id,
                "sector": i.sector,
                "nombre": i.paciente.nombre,
                "dni": i.paciente.dni,
                "diagnostico": i.diagnostico,
                "fecha_ingreso": i.fecha_ingreso,
                "estado": i.get_estado_display(),
                "estado_color": _estado_color(i.get_estado_display()),
            }
        )

    contexto = {
        "cobertura": cobertura,
        "internaciones": internaciones,
    }
    return render(request, "internaciones/censo_cobertura.html", contexto)

def hc_lista_pacientes(request):
    qs = Paciente.objects.select_related("cobertura").all()
    texto = request.GET.get("search") or ""
    if texto:
        qs = qs.filter(
            Q(nombre__icontains=texto)
            | Q(dni__icontains=texto)
            | Q(nro_afiliado__icontains=texto)
        )

    pacientes = []
    for p in qs:
        pacientes.append(
            {
                "id": p.id,
                "nombre": p.nombre,
                "dni": p.dni,
                "cobertura": p.cobertura.nombre if p.cobertura else "",
                "afiliado": p.nro_afiliado,
            }
        )

    contexto = {"pacientes": pacientes}
    return render(request, "internaciones/hc_lista_pacientes.html", contexto)

def hc_detalle_paciente(request, pk):
    paciente = get_object_or_404(Paciente.objects.select_related("cobertura"), pk=pk)

    if request.method == "POST":
        form = HCDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.paciente = paciente
            if not doc.nombre_visible:
                doc.nombre_visible = doc.archivo.name
            doc.save()
            return redirect("hc_detalle_paciente", pk=paciente.pk)
    else:
        form = HCDocumentForm()

    docs = HCDocument.objects.filter(paciente=paciente).order_by("-fecha")

    tabs = {
        "autorizaciones": [],
        "epicrisis": [],
        "boletin": [],
        "evol_med": [],
        "evol_enf": [],
        "interconsultas": [],
        "laboratorio": [],
        "imagenes": [],
        "otros": [],
    }
    for d in docs:
        tabs[d.tab].append(d)

    contexto = {
        "paciente": paciente,
        "form": form,
        "tabs": tabs,
    }
    return render(request, "internaciones/hc_detalle_paciente.html", contexto)
