import google.generativeai as genai
from django.conf import settings
from .models import Habilidade

def gerar_plano_de_aula_com_ia(componente, serie, tema):
    try:
        # Configura a API Key a partir das configurações do Django
        genai.configure(api_key=settings.GOOGLE_API_KEY)

        # Busca habilidades da BNCC relacionadas ao componente para enriquecer o prompt
        habilidades_bncc = Habilidade.objects.filter(componente=componente)
        lista_habilidades_str = "\n".join([f"- {h.codigo}: {h.descricao}" for h in habilidades_bncc])

        # Cria o prompt detalhado para a IA
        prompt = f"""
        **Instrução:** Você é um especialista em pedagogia e na BNCC do Ensino Médio. Crie um plano de aula detalhado e criativo.

        **Formato de Saída:** Use Markdown para formatação com títulos, listas e negrito. O plano deve conter as seguintes seções:
        - Título da Aula:
        - Objetivos de Aprendizagem: (Liste 3 objetivos claros)
        - Habilidades da BNCC Relacionadas: (Selecione 1 ou 2 códigos mais relevantes da lista abaixo e descreva como serão trabalhados)
        - Metodologia e Desenvolvimento: (Descreva um roteiro passo a passo: introdução, desenvolvimento com atividades práticas e fechamento)
        - Recursos Necessários:
        - Forma de Avaliação:

        **Dados da Aula:**
        - **Componente Curricular:** {componente.nome}
        - **Série:** {serie}
        - **Tema da Aula:** {tema}

        **Lista de Habilidades BNCC Disponíveis para este Componente:**
        {lista_habilidades_str if lista_habilidades_str else "Nenhuma habilidade específica cadastrada."}
        """

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
        return "Desculpe, ocorreu um erro ao tentar gerar o plano de aula. Verifique sua chave de API e tente novamente."