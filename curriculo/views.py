from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from weasyprint import HTML
import datetime

from .forms import (
    GeradorPlanoForm, PerfilProfessorForm,
    AreaForm, ComponenteForm
)
from .ia_service import gerar_plano_de_aula_com_ia  # Importa a versão revertida que faremos a seguir
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


# --- View do Gerador (REVERTIDA) ---
@login_required(login_url='login')
def gerador_view(request):
    form = GeradorPlanoForm(request.POST or None)
    erro_ia = None

    if request.method == 'POST' and form.is_valid():
        # Coleta apenas UM componente
        componente = form.cleaned_data['componente_curricular']

        # Coleta os outros dados
        serie_valor = form.cleaned_data['serie']
        serie_texto = dict(form.fields['serie'].choices)[serie_valor]
        tema = form.cleaned_data['tema_aula']
        contexto = form.cleaned_data['contexto']

        # Envia UM componente para a IA (a função ia_service será revertida também)
        plano_data_dict = gerar_plano_de_aula_com_ia(componente, serie_texto, tema, contexto)

        if "erro" not in plano_data_dict:
            plano_salvo = PlanoDeAula.objects.create(
                autor=request.user,
                componente=componente,  # Salva o componente único
                serie=serie_texto,
                tema_aula=tema,
                conteudo_gerado=plano_data_dict  # Salva o JSON simples
            )
            return redirect('plano_detalhe', plano_id=plano_salvo.id)
        else:
            erro_ia = plano_data_dict.get('erro', 'Um erro desconhecido ocorreu na IA.')

    context = {'form': form, 'erro_ia': erro_ia}
    return render(request, 'curriculo/gerador.html', context)


# --- View de Detalhes (REVERTIDA - contexto simplificado) ---
@login_required(login_url='login')
def plano_detalhe_view(request, plano_id):
    try:
        plano = PlanoDeAula.objects.get(id=plano_id, autor=request.user)
        # Contexto volta a ser simples, sem dia_map
        context = {'plano': plano}
        return render(request, 'curriculo/plano_detalhe.html', context)
    except PlanoDeAula.DoesNotExist:
        messages.error(request, "Plano de aula não encontrado ou você não tem permissão para vê-lo.")
        return redirect('gerador')


# --- View do PDF (REVERTIDA - contexto simplificado) ---
@login_required(login_url='login')
def gerar_pdf_view(request, plano_id):
    try:
        plano = PlanoDeAula.objects.get(id=plano_id, autor=request.user)
        perfil = request.user.perfil
        # Contexto volta a ser simples, sem dia_map
        context = {
            'plano': plano,
            'hoje': datetime.date.today(),
            'perfil': perfil,
            'request': request
        }
        html_string = render_to_string('curriculo/plano_pdf.html', context)
        pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="plano_de_aula_{plano.id}.pdf"'
        return response
    except PlanoDeAula.DoesNotExist:
        return HttpResponse("Plano de aula não encontrado ou você não tem permissão.", status=404)
    except PerfilProfessor.DoesNotExist:
        return HttpResponse("Perfil do professor não encontrado.", status=404)


# --- Views CRUD (sem alterações) ---
# ... (código das views CRUD existente) ...
@login_required(login_url='login')
def listar_areas(request):
    # ... (código existente) ...
    areas = AreaDoConhecimento.objects.all().order_by('nome')
    return render(request, 'curriculo/crud/listar_areas.html', {'areas': areas})


@login_required(login_url='login')
def criar_area(request):
    # ... (código existente) ...
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
    # ... (código existente) ...
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
    # ... (código existente) ...
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
    # ... (código existente) ...
    componentes = ComponenteCurricular.objects.select_related('area').all().order_by('nome')
    return render(request, 'curriculo/crud/listar_componentes.html', {'componentes': componentes})


@login_required(login_url='login')
def criar_componente(request):
    # ... (código existente) ...
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
    # ... (código existente) ...
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
    # ... (código existente) ...
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