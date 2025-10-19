from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Modelos existentes
class AreaDoConhecimento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nome

class ComponenteCurricular(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    area = models.ForeignKey(AreaDoConhecimento, on_delete=models.CASCADE)
    def __str__(self): return f'{self.nome} ({self.area.nome})'

class Habilidade(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField()
    serie = models.CharField(max_length=50)
    componente = models.ForeignKey(ComponenteCurricular, on_delete=models.CASCADE)
    def __str__(self): return self.codigo

class PlanoDeAula(models.Model):
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='planos_criados')
    componente = models.ForeignKey(ComponenteCurricular, on_delete=models.SET_NULL, null=True)
    serie = models.CharField(max_length=100) # Mantemos a série específica do plano
    tema_aula = models.CharField(max_length=200)
    conteudo_gerado = models.JSONField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Plano de {self.tema_aula} ({self.data_criacao.strftime('%d/%m/%Y')})"

# Modelo do Perfil ATUALIZADO
class PerfilProfessor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nome_completo = models.CharField('Nome Completo', max_length=255, blank=True, null=True)
    escola = models.CharField('Escola Padrão', max_length=200, blank=True, null=True, default="SAUL BENNESBY")
    turma_padrao = models.CharField('Turma Padrão', max_length=50, blank=True, null=True)
    turno_padrao = models.CharField('Turno Padrão', max_length=50, blank=True, null=True)
    # NOVOS CAMPOS PARA O PDF
    duracao_padrao = models.CharField('Duração Padrão da Aula', max_length=50, blank=True, null=True, default="4 horas")
    espaco_padrao = models.CharField('Espaço Padrão', max_length=100, blank=True, null=True, default="Sala e pátio escolar")

    def __str__(self):
        return f"Perfil de {self.user.username}"

@receiver(post_save, sender=User)
def criar_ou_atualizar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilProfessor.objects.create(user=instance)
    try:
        instance.perfil.save()
    except PerfilProfessor.DoesNotExist:
         PerfilProfessor.objects.create(user=instance)