from django import forms
from .models import ComponenteCurricular, PerfilProfessor, AreaDoConhecimento


# Formulário do gerador REVERTIDO para um componente
class GeradorPlanoForm(forms.Form):
    # Campo único de componente curricular
    componente_curricular = forms.ModelChoiceField(
        queryset=ComponenteCurricular.objects.all().order_by('nome'),
        label="Componente Curricular (Disciplina)",
        empty_label="Selecione uma disciplina",
        widget=forms.Select(attrs={'class': 'form-input'})  # Revertido de SelectMultiple
    )

    # Campos restantes
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
    tema_aula = forms.CharField(
        label="Tema da Aula", max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Ciclo da Água', 'class': 'form-input'})
    )
    contexto = forms.CharField(
        label="Contexto Adicional (Opcional)", required=False,
        widget=forms.Textarea(
            attrs={'placeholder': 'Ex: Focar em atividades práticas...', 'class': 'form-textarea', 'rows': 4})
    )


# Formulário do Perfil (versão anterior já estava correta)
class PerfilProfessorForm(forms.ModelForm):
    class Meta:
        model = PerfilProfessor
        fields = ['nome_completo', 'escola', 'turma_padrao', 'turno_padrao', 'duracao_padrao', 'espaco_padrao']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-input'}),
            'escola': forms.TextInput(attrs={'class': 'form-input'}),
            'turma_padrao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 5º B'}),
            'turno_padrao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 2 (para Vespertino)'}),
            'duracao_padrao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 4 horas'}),
            'espaco_padrao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Sala e pátio escolar'}),
        }
        labels = {
            'nome_completo': 'Nome Completo', 'escola': 'Escola Padrão',
            'turma_padrao': 'Turma Padrão', 'turno_padrao': 'Turno Padrão',
            'duracao_padrao': 'Duração Padrão da Aula', 'espaco_padrao': 'Espaço Padrão de Aula',
        }


# Formulários CRUD (versão anterior já estava correta)
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
        widgets = {'nome': forms.TextInput(attrs={'class': 'form-input'}),
                   'area': forms.Select(attrs={'class': 'form-input'})}
        labels = {'nome': 'Nome do Componente (Disciplina)', 'area': 'Área do Conhecimento'}