import google.generativeai as genai
from django.conf import settings
import json


# Função REVERTIDA para receber UM componente
def gerar_plano_de_aula_com_ia(componente, serie, tema, contexto):
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)

        contexto_professor = contexto if contexto else "Nenhum."

        # PROMPT REVERTIDO PARA A ESTRUTURA SIMPLES
        prompt = f"""
        **Instrução:** Você é um especialista em pedagogia e no **Referencial Curricular de Rondônia (RCRO)**. Sua tarefa é gerar o conteúdo para um plano de oficina semanal completo.

        **Formato de Saída OBRIGATÓRIO:** Responda APENAS com um objeto JSON válido, sem nenhum texto ou formatação adicional antes ou depois dele (sem ```json ... ```).

        **Dados para o Plano de Aula:**
        - **Tema da Semana:** {tema}
        - **Componente Curricular:** {componente.nome}
        - **Série:** {serie}
        - **Contexto Adicional do Professor:** {contexto_professor}

        **Estrutura JSON de Saída ESPERADA (OBJETO POR DIA):**
        {{
          "segunda": {{
            "eixo_tematico": "Liste os eixos temáticos do RCRO para Segunda-feira.",
            "habilidades": "Liste os códigos de habilidades do RCRO para Segunda-feira.",
            "objeto_conhecimento": "Liste os objetos de conhecimento do RCRO para Segunda-feira.",
            "rotina": "Descreva a rotina para Segunda-feira."
          }},
          "terca": {{ "eixo_tematico": "...", "habilidades": "...", "objeto_conhecimento": "...", "rotina": "..." }},
          "quarta": {{ "eixo_tematico": "...", "habilidades": "...", "objeto_conhecimento": "...", "rotina": "..." }},
          "quinta": {{ "eixo_tematico": "...", "habilidades": "...", "objeto_conhecimento": "...", "rotina": "..." }},
          "sexta": {{ "eixo_tematico": "...", "habilidades": "...", "objeto_conhecimento": "...", "rotina": "..." }},
          "metodologia": "Metodologia geral da semana.",
          "recursos_didaticos": "Lista de recursos gerais.",
          "avaliacao": "Descrição da avaliação semanal."
        }}
        """

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)

        cleaned_response = response.text.strip().lstrip('```json').rstrip('```')

        # Validação simples
        try:
            parsed_json = json.loads(cleaned_response)
            dias = ["segunda", "terca", "quarta", "quinta", "sexta"]
            # Verifica se as chaves dos dias existem e são dicionários (não listas)
            if not all(isinstance(parsed_json.get(dia), dict) for dia in dias):
                raise ValueError("Estrutura JSON inválida: Chaves dos dias devem conter objetos.")
            return parsed_json
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Erro ao processar JSON da IA: {e}")
            print(f"Resposta recebida: {cleaned_response}")
            return {
                "erro": f"A resposta da IA não é um JSON válido ou tem estrutura incorreta. Resposta: {cleaned_response}"}

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
        return {"erro": f"Ocorreu um erro na API: {e}"}