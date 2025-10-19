# curriculo/views.py (Revertido para estrutura simples de contexto)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from weasyprint import HTML
import datetime
import json

from .forms import (
    GeradorPlanoForm, PerfilProfessorForm,
    AreaForm, ComponenteForm
)
# Certifique-se que ia_service está na versão CONSOLIDADA
from .ia_service import gerar_plano_de_aula_com_ia
from .models import PlanoDeAula, PerfilProfessor, AreaDoConhecimento, ComponenteCurricular


# --- Views de Autenticação e Perfil (sem alterações) ---
def login_view(request):
    # ... (código existente) ...
    erro = None
    if request.method == 'POST':
        usuario_form = request.POST.get('username')
        senha_form = request.POST.get('password')
        user = authenticate(request, username=usuario_form, password=senha_form)
        if user is not None:
            login(request, user)
            return redirect('gerador')
        else:
            erro = "Nome de usuário ou senha inválidos."
    return render(request, 'curriculo/login.html', {'erro': erro})


def registrar_view(request):
    # ... (código existente) ...
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('gerador')
    else:
        form = UserCreationForm()
    return render(request, 'curriculo/registrar.html', {'form': form})


def logout_view(request):
    # ... (código existente) ...
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def perfil_view(request):
    # ... (código existente) ...
    perfil = request.user.perfil
    if request.method == 'POST':
        form = PerfilProfessorForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('perfil')
    else:
        form = PerfilProfessorForm(instance=perfil)
    context = {'form': form}
    return render(request, 'curriculo/perfil.html', context)


# --- View do Gerador (Adaptada para enviar estrutura à IA consolidada) ---
@login_required(login_url='login')
def gerador_view(request):
    erro_ia = None
    if request.method == 'POST':
        form = GeradorPlanoForm(request.POST)
        if form.is_valid():
            json_data_str = form.cleaned_data.get('componentes_temas_json', '{}')
            try:
                componentes_temas_por_dia = json.loads(json_data_str)
            except json.JSONDecodeError:
                messages.error(request, "Erro ao processar os componentes selecionados.")
                componentes_temas_por_dia = {}

            serie_valor = form.cleaned_data['serie']
            serie_texto = dict(form.fields['serie'].choices)[serie_valor]
            contexto = form.cleaned_data['contexto']

            # Prepara a estrutura para enviar à IA (ainda precisamos saber quais componentes foram selecionados)
            componentes_objetos_por_dia = {}
            componentes_selecionados_ids = set()
            for dia, items in componentes_temas_por_dia.items():
                componentes_objetos_por_dia[dia] = []
                for item in items:
                    try:
                        comp_id = int(item['componente_id'])
                        componentes_selecionados_ids.add(comp_id)
                    except (ValueError, KeyError):
                        continue

            componentes_db = ComponenteCurricular.objects.in_bulk(componentes_selecionados_ids)

            componentes_para_ia = {}  # IA agora só precisa saber os NOMES para consolidar
            for dia, items in componentes_temas_por_dia.items():
                componentes_para_ia[dia] = []
                for item in items:
                    try:
                        comp_id = int(item['componente_id'])
                        comp_obj = componentes_db.get(comp_id)
                        if comp_obj:
                            # A IA consolidada só precisa do objeto componente
                            # O 'tema' específico não é mais usado diretamente pela IA consolidada, mas pode ser útil no futuro
                            componentes_para_ia[dia].append({
                                'componente': comp_obj,
                                'tema': item.get('tema', '')
                            })
                    except (ValueError, KeyError):
                        continue

            # Chama a IA CONSOLIDADA
            plano_data_dict = gerar_plano_de_aula_com_ia(componentes_para_ia, serie_texto, contexto)

            if plano_data_dict and "erro" not in plano_data_dict:
                primeiro_componente = None
                for dia in ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']:
                    if componentes_para_ia.get(dia):
                        primeiro_componente = componentes_para_ia[dia][0]['componente']
                        break

                plano_salvo = PlanoDeAula.objects.create(
                    autor=request.user,
                    componente=primeiro_componente,
                    serie=serie_texto,
                    tema_aula=f"Plano Semanal Consolidado - {serie_texto}",  # Ajusta o tema
                    conteudo_gerado=plano_data_dict  # Salva o JSON simples retornado
                )
                return redirect('plano_detalhe', plano_id=plano_salvo.id)
            else:
                erro_ia = plano_data_dict.get('erro', 'Um erro desconhecido ocorreu na IA.') if isinstance(
                    plano_data_dict, dict) else 'Erro inesperado na resposta da IA.'

    else:  # Método GET
        form = GeradorPlanoForm()

    todos_componentes = ComponenteCurricular.objects.all().order_by('nome')
    dias_semana = {  # Ainda necessário para o template do gerador
        'segunda': 'Segunda-feira', 'terca': 'Terça-feira', 'quarta': 'Quarta-feira',
        'quinta': 'Quinta-feira', 'sexta': 'Sexta-feira', 'sabado': 'Sábado'
    }
    context = {
        'form': form, 'erro_ia': erro_ia,
        'todos_componentes': todos_componentes, 'dias_semana': dias_semana
    }
    return render(request, 'curriculo/gerador.html', context)


# --- View de Detalhes (REVERTIDA para contexto simples) ---
@login_required(login_url='login')
def plano_detalhe_view(request, plano_id):
    try:
        plano = PlanoDeAula.objects.get(id=plano_id, autor=request.user)
        # REMOVE dia_map do contexto
        context = {'plano': plano}
        return render(request, 'curriculo/plano_detalhe.html', context)  # Usa o template revertido
    except PlanoDeAula.DoesNotExist:
        messages.error(request, "Plano de aula não encontrado ou você não tem permissão.")
        return redirect('gerador')


# --- View do PDF (REVERTIDA para contexto simples) ---
@login_required(login_url='login')
def gerar_pdf_view(request, plano_id):
    try:
        plano = PlanoDeAula.objects.get(id=plano_id, autor=request.user)
        perfil = request.user.perfil
        # REMOVE dia_map do contexto
        context = {
            'plano': plano,
            'hoje': datetime.date.today(),
            'perfil': perfil,
            'request': request
        }
        html_string = render_to_string('curriculo/plano_pdf.html', context)  # Usa o template revertido
        pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="plano_de_aula_{plano.id}.pdf"'
        return response
    except PlanoDeAula.DoesNotExist:
        return HttpResponse("Plano de aula não encontrado ou você não tem permissão.", status=404)
    except PerfilProfessor.DoesNotExist:
        return HttpResponse("Perfil do professor não encontrado.", status=404)


# --- Views CRUD (sem alterações) ---
# ... (código CRUD existente) ...
@login_required(login_url='login')
def listar_areas(request):
    areas = AreaDoConhecimento.objects.all().order_by('nome')
    return render(request, 'curriculo/crud/listar_areas.html', {'areas': areas})


@login_required(login_url='login')
def criar_area(request):
    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área do conhecimento criada com sucesso!')
            return redirect('listar_areas')
    else:
        form = AreaForm()
    return render(request, 'curriculo/crud/form_area.html', {'form': form, 'titulo': 'Nova Área do Conhecimento'})


@login_required(login_url='login')
def editar_area(request, pk):
    area = get_object_or_404(AreaDoConhecimento, pk=pk)
    if request.method == 'POST':
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área do conhecimento atualizada com sucesso!')
            return redirect('listar_areas')
    else:
        form = AreaForm(instance=area)
    return render(request, 'curriculo/crud/form_area.html', {'form': form, 'titulo': 'Editar Área do Conhecimento'})


@login_required(login_url='login')
def deletar_area(request, pk):
    area = get_object_or_404(AreaDoConhecimento, pk=pk)
    if request.method == 'POST':
        try:
            area.delete()
            messages.success(request, 'Área do conhecimento excluída com sucesso!')
        except Exception as e:
            messages.error(request,
                           f'Não foi possível excluir a área. Verifique se ela não está sendo usada por algum componente. Erro: {e}')
        return redirect('listar_areas')
    return render(request, 'curriculo/crud/confirmar_delete.html', {'objeto': area, 'tipo': 'Área do Conhecimento'})


@login_required(login_url='login')
def listar_componentes(request):
    componentes = ComponenteCurricular.objects.select_related('area').all().order_by('nome')
    return render(request, 'curriculo/crud/listar_componentes.html', {'componentes': componentes})


@login_required(login_url='login')
def criar_componente(request):
    if request.method == 'POST':
        form = ComponenteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Componente curricular criado com sucesso!')
            return redirect('listar_componentes')
    else:
        form = ComponenteForm()
    return render(request, 'curriculo/crud/form_componente.html',
                  {'form': form, 'titulo': 'Novo Componente Curricular'})


@login_required(login_url='login')
def editar_componente(request, pk):
    componente = get_object_or_404(ComponenteCurricular, pk=pk)
    if request.method == 'POST':
        form = ComponenteForm(request.POST, instance=componente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Componente curricular atualizado com sucesso!')
            return redirect('listar_componentes')
    else:
        form = ComponenteForm(instance=componente)
    return render(request, 'curriculo/crud/form_componente.html',
                  {'form': form, 'titulo': 'Editar Componente Curricular'})


@login_required(login_url='login')
def deletar_componente(request, pk):
    componente = get_object_or_404(ComponenteCurricular, pk=pk)
    if request.method == 'POST':
        try:
            componente.delete()
            messages.success(request, 'Componente curricular excluído com sucesso!')
        except Exception as e:
            messages.error(request,
                           f'Não foi possível excluir o componente. Verifique se ele não está em uso. Erro: {e}')
        return redirect('listar_componentes')
    return render(request, 'curriculo/crud/confirmar_delete.html',
                  {'objeto': componente, 'tipo': 'Componente Curricular'})