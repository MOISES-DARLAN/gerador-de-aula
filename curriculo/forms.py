from django import forms
from .models import ComponenteCurricular, PerfilProfessor, AreaDoConhecimento

# Formulário do gerador REESTRUTURADO para receber JSON do frontend
class GeradorPlanoForm(forms.Form):
    # Campo oculto para receber a estrutura JSON montada pelo JavaScript
    componentes_temas_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Campos gerais que permanecem
    serie = forms.ChoiceField(
        label="Série/Ano",
        choices=[
            ('EF1', '1º Ano - Ensino Fundamental'), ('EF2', '2º Ano - Ensino Fundamental'),
            ('EF3', '3º Ano - Ensino Fundamental'), ('EF4', '4º Ano - Ensino Fundamental'),
            ('EF5', '5º Ano - Ensino Fundamental'), ('EF6', '6º Ano - Ensino Fundamental'),
            ('EF7', '7º Ano - Ensino Fundamental'), ('EF8', '8º Ano - Ensino Fundamental'),
            ('EF9', '9º Ano - Ensino Fundamental'), ('EM1', '1ª Série - Ensino Médio'),
            ('EM2', '2ª Série - Ensino Médio'), ('EM3', '3ª Série - Ensino Médio'),
        ],
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    # Tema geral foi removido, pois agora é por componente/dia
    contexto = forms.CharField(
        label="Contexto Adicional (Opcional)", required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Instruções gerais para a IA...', 'class': 'form-textarea', 'rows': 4})
    )

# --- Formulários inalterados ---
class PerfilProfessorForm(forms.ModelForm):
    class Meta:
        model = PerfilProfessor
        fields = ['nome_completo', 'escola', 'turma_padrao', 'turno_padrao', 'duracao_padrao', 'espaco_padrao']
        # ... widgets e labels existentes ...
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-input'}),
            'escola': forms.TextInput(attrs={'class': 'form-input'}),
            'turma_padrao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 5º B'}),
            'turno_padrao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 2 (Vespertino)'}),
            'duracao_padrao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 4 horas'}),
            'espaco_padrao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Sala e pátio escolar'}),
        }
        labels = {
            'nome_completo': 'Nome Completo', 'escola': 'Escola Padrão',
            'turma_padrao': 'Turma Padrão', 'turno_padrao': 'Turno Padrão',
            'duracao_padrao': 'Duração Padrão da Aula', 'espaco_padrao': 'Espaço Padrão de Aula',
        }

class AreaForm(forms.ModelForm):
    class Meta:
        model = AreaDoConhecimento
        fields = ['nome']
        widgets = {'nome': forms.TextInput(attrs={'class': 'form-input'})}
        labels = {'nome': 'Nome da Área do Conhecimento'}

class ComponenteForm(forms.ModelForm):
    class Meta:
        model = ComponenteCurricular
        fields = ['nome', 'area']
        widgets = {'nome': forms.TextInput(attrs={'class': 'form-input'}), 'area': forms.Select(attrs={'class': 'form-input'})}
        labels = {'nome': 'Nome do Componente (Disciplina)', 'area': 'Área do Conhecimento'}