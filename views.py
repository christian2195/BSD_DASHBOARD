from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.contrib import messages
from .models import BSDRegistro
from .forms import ExcelUploadForm

@login_required
def dashboard_view(request):
    registros = BSDRegistro.objects.all()
    
    total_monto = registros.aggregate(Sum('monto_total'))['monto_total__sum'] or 0
    total_proyectos = registros.count()
    total_articulos = registros.aggregate(Sum('cant_articulos_dotados'))['cant_articulos_dotados__sum'] or 0
    
    estados = registros.values('ejecutada').annotate(
        count=Count('id'),
        monto_total=Sum('monto_total')
    )
    
    vertices = registros.values('vertice').annotate(
        count=Count('id'),
        monto_total=Sum('monto_total')
    )
    
    top_instituciones = registros.order_by('-monto_total')[:10]
    
    context = {
        'total_monto': total_monto,
        'total_proyectos': total_proyectos,
        'total_articulos': total_articulos,
        'estados': list(estados),
        'vertices': list(vertices),
        'top_instituciones': top_instituciones,
        'registros': registros,
    }
    
    return render(request, 'dashboard_app/dashboard.html', context)

@login_required
def upload_data(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            result = form.process_excel()
            
            if result['success']:
                messages.success(request, f'Datos cargados exitosamente: {result["total"]} registros procesados (Creados: {result["records_created"]}, Actualizados: {result["records_updated"]})')
                return redirect('dashboard')
            else:
                messages.error(request, f'Error al procesar el archivo: {result["error"]}')
    else:
        form = ExcelUploadForm()
    
    registros = BSDRegistro.objects.all()
    return render(request, 'dashboard_app/upload.html', {'form': form, 'registros': registros})

def index_view(request):
    return render(request, 'dashboard_app/index.html')

@login_required
def api_dashboard_data(request):
    registros = BSDRegistro.objects.all()
    
    data = {
        'estados': list(registros.values('ejecutada').annotate(
            count=Count('id'),
            monto=Sum('monto_total')
        )),
        'vertices': list(registros.values('vertice').annotate(
            count=Count('id'),
            monto=Sum('monto_total')
        )),
    }
    
    return JsonResponse(data)
