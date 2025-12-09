from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Seleccionar archivo Excel',
        help_text='Formatos soportados: .xlsx, .xls'
    )
    replace_data = forms.BooleanField(
        required=False,
        initial=False,
        label='Reemplazar todos los datos existentes'
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']
        
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError('Solo se permiten archivos Excel (.xlsx, .xls)')
        
        if file.size > 10 * 1024 * 1024:
            raise forms.ValidationError('El archivo no debe superar los 10MB')
        
        return file
