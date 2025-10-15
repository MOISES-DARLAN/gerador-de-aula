from django.shortcuts import render
from .forms import GeradorPlanoForm
from .ia_service import gerar_plano_de_aula_com_ia # Importe a nova função

def gerador_view(request):
    plano_gerado = None # Inicializa a variável
    form = GeradorPlanoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        componente = form.cleaned_data['componente_curricular']
        serie_tuple = form.fields['serie'].choices[int(form.cleaned_data['serie']) - 1]
        serie_texto = serie_tuple[1]
        tema = form.cleaned_data['tema_aula']

        # Chama o serviço de IA
        plano_gerado = gerar_plano_de_aula_com_ia(componente, serie_texto, tema)

    context = {
        'form': form,
        'plano_gerado': plano_gerado,
    }
    return render(request, 'curriculo/gerador.html', context)