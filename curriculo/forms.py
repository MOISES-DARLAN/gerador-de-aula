from django import forms
from .models import ComponenteCurricular

class GeradorPlanoForm(forms.Form):
    
    componente_curricular = forms.ModelChoiceField(
        queryset=ComponenteCurricular.objects.all().order_by('nome'),
        label="Componente Curricular (Disciplina)",
        empty_label="Selecione uma disciplina",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    
    serie = forms.ChoiceField(
        label="Série",
        choices=[
            ('1', '1ª Série do Ensino Médio'),
            ('2', '2ª Série do Ensino Médio'),
            ('3', '3ª Série do Ensino Médio'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    
    tema_aula = forms.CharField(
        label="Tema da Aula",
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: Fotossíntese e Respiração Celular',
            'class': 'form-input'
        })
    )