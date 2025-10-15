from django.db import models


class AreaDoConhecimento(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class ComponenteCurricular(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
    
    area = models.ForeignKey(AreaDoConhecimento, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nome} ({self.area.nome})'


class Habilidade(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField()
    serie = models.CharField(max_length=50)
    
    componente = models.ForeignKey(ComponenteCurricular, on_delete=models.CASCADE)

    def __str__(self):
        return self.codigo