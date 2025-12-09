from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.contrib import messages
from .models import BSDRegistro
from .forms import ExcelUploadForm
import pandas as pd
import math
import traceback

def parse_formula(value):
    """Convierte fórmulas Excel simples en valores numéricos"""
    if isinstance(value, str):
        if value.startswith('='):
            # Manejar fórmulas simples como =100+200
            try:
                if '+' in value:
                    parts = value.replace('=', '').split('+')
                    return float(parts[0].strip()) + float(parts[1].strip())
                elif '-' in value:
                    parts = value.replace('=', '').split('-')
                    return float(parts[0].strip()) - float(parts[1].strip())
            except:
                return 0.0
        # Si es un string que representa un número
        try:
            return float(value)
        except:
            return 0.0
    elif pd.isna(value):
        return 0.0
    elif isinstance(value, (int, float)):
        return float(value)
    return 0.0

def index_view(request):
    return render(request, 'dashboard_app/index.html')

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
            excel_file = request.FILES['excel_file']
            replace_data = request.POST.get('replace_data', False)
            
            try:
                # Leer el archivo Excel
                df = pd.read_excel(excel_file, sheet_name='bsd')
                
                if replace_data:
                    BSDRegistro.objects.all().delete()
                    messages.info(request, 'Datos anteriores eliminados.')
                
                records_created = 0
                records_updated = 0
                
                for index, row in df.iterrows():
                    # Saltar filas vacías o sin ITEM
                    if pd.isna(row.get('ITEM')):
                        continue
                    
                    # Buscar o crear el registro
                    item = int(row['ITEM']) if not pd.isna(row['ITEM']) else 0
                    
                    # Procesar cada campo
                    defaults = {
                        'institucion': str(row.get('INSTITUCIÓN', ''))[:500],
                        'proyecto': str(row.get('PROYECTO', ''))[:100] if not pd.isna(row.get('PROYECTO')) else None,
                        'cant_articulos_dotados': int(row.get('CANT. ARTICULOS DOTADOS', 0)) if not pd.isna(row.get('CANT. ARTICULOS DOTADOS')) else 0,
                        'cant_articulos_faltantes': int(row.get('CANT. ARTICULOS FALTANTES', 0)) if not pd.isna(row.get('CANT. ARTICULOS FALTANTES')) else 0,
                        'monto_total': parse_formula(row.get('MONTO TOTAL', 0)),
                        'monto_total_cobrado': parse_formula(row.get('MONTO TOTAL COBRADO', 0)),
                        'monto_total_pendiente': parse_formula(row.get('MONTO TOTAL PENDIENTE', 0)),
                        'vertice': str(row.get('VÉRTICE', 'V1'))[:10],
                        'v1': parse_formula(row.get('V1', 0)),
                        'v3': parse_formula(row.get('V3', 0)),
                        'v4': parse_formula(row.get('V4', 0)),
                        'ejecutada': str(row.get('EJECUTADA', 'POR DOTAR'))[:20],
                        'centros_salud': parse_formula(row.get('CENTROS DE SALUD (V3)', 0)),
                        'educacion': parse_formula(row.get('EDUCACION', 0)),
                        'deporte_recreacion': parse_formula(row.get('DEPORTE, RECREACION, ESPARCIMIENTO Y OTROS', 0)),
                        'unidades_militares': parse_formula(row.get('UNIDADES MILITARES', 0)),
                    }
                    
                    # Asegurar que los valores de opciones sean válidos
                    if defaults['vertice'] not in ['V1', 'V3', 'V4']:
                        defaults['vertice'] = 'V1'
                    
                    if defaults['ejecutada'] not in ['EJECUTADA', 'EN EJECUCION', 'POR DOTAR']:
                        defaults['ejecutada'] = 'POR DOTAR'
                    
                    obj, created = BSDRegistro.objects.update_or_create(
                        item=item,
                        defaults=defaults
                    )
                    
                    if created:
                        records_created += 1
                    else:
                        records_updated += 1
                
                messages.success(request, f'Archivo procesado correctamente. Creados: {records_created}, Actualizados: {records_updated}')
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
        else:
            messages.error(request, 'Formulario inválido. Verifique el archivo seleccionado.')
    
    else:
        form = ExcelUploadForm()
    
    return render(request, 'dashboard_app/upload.html', {'form': form})

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
