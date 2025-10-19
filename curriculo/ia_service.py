import google.generativeai as genai
from django.conf import settings
import json

# Mapeamento de abreviações
ABREVIACOES = {
    'Língua Portuguesa': 'LP', 'Arte': 'AR', 'Educação Física': 'EF',
    'Língua Inglesa': 'LI', 'Matemática': 'MA', 'Biologia': 'BIO',
    'Física': 'FIS', 'Química': 'QUI', 'História': 'HI',
    'Geografia': 'GE', 'Filosofia': 'FIL', 'Sociologia': 'SOC',
}


def gerar_plano_de_aula_com_ia(componentes_para_ia, serie, contexto):
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)

        contexto_professor = contexto if contexto else "Nenhum."

        estrutura_diaria_prompt = ""
        componentes_nomes_geral = set()
        for dia, items in componentes_para_ia.items():
            if items:
                nomes_dia = [item['componente'].nome for item in items]
                estrutura_diaria_prompt += f"**{dia.capitalize()}**: {', '.join(nomes_dia)}\n"
                for nome in nomes_dia: componentes_nomes_geral.add(nome)
            else:
                estrutura_diaria_prompt += f"**{dia.capitalize()}**: Nenhum componente selecionado\n"

        abreviacoes_prompt = "\n".join([f"- {nome}: {ABREVIACOES.get(nome, nome[:3].upper())}"
                                        for nome in sorted(list(componentes_nomes_geral))])

        # PROMPT COM AJUSTE NA FORMATAÇÃO DE HABILIDADES
        prompt = f"""
        **Instrução:** Você é um especialista em pedagogia e no **Referencial Curricular de Rondônia (RCRO)**. Gere um plano de oficina semanal CONCISO, seguindo ESTRITAMENTE as regras de formatação para cada campo.

        **Formato de Saída OBRIGATÓRIO:** Responda APENAS com um objeto JSON válido, sem nenhum texto ou formatação adicional (sem ```json ... ```).

        **Dados Gerais:**
        - **Série/Ano:** {serie}
        - **Contexto Adicional:** {contexto_professor}

        **Componentes por Dia:**
        {estrutura_diaria_prompt}

        **Abreviações a serem usadas (APENAS para Objeto do Conhecimento):**
        {abreviacoes_prompt if abreviacoes_prompt else "Nenhuma"}

        **REGRAS DE FORMATAÇÃO ESTRITAS:**
        1.  **CONCISÃO:** Seja direto e use frases curtas.
        2.  **`eixo_tematico`:** Liste APENAS os nomes dos eixos temáticos. Separe múltiplos com \\n. NÃO use abreviações de componentes.
        3.  **`habilidades`:** Liste APENAS os CÓDIGOS PADRÃO das habilidades (ex: EF05MA17, EM13LP01). Separe múltiplos códigos com \\n. **NÃO inclua o prefixo regional 'RO-'**. NÃO use abreviações de componentes e NÃO inclua descrições.
        4.  **`objeto_conhecimento`:** Liste os objetos. PARA CADA objeto, coloque a abreviação do componente antes (Ex: "LP: Gênero textual...\\nMA: Operações..."). Separe com \\n.
        5.  **`rotina`:** Descreva a rotina de forma concisa. Separe itens com \\n. NÃO use abreviações de componentes.
        6.  **Campos Gerais:** Mantenha `metodologia`, `recursos_didaticos`, `avaliacao` no nível superior, com descrições GERAIS e CONCISAS.

        **Estrutura JSON de Saída ESPERADA:**
        {{
          "segunda": {{
            "eixo_tematico": "Nome Eixo 1\\nNome Eixo 2",
            "habilidades": "EF05LP28\\nEF05MA17", // Exemplo SEM 'RO-'
            "objeto_conhecimento": "LP: Objeto LP...\\nMA: Objeto MA...",
            "rotina": "Acolhida.\\nLeitura deleite.\\nAtividade X.\\n..."
          }},
          "terca": {{ ... seguindo as mesmas regras ... }},
          "quarta": {{ ... }},
          "quinta": {{ ... }},
          "sexta": {{ ... }},
          "sabado": {{ ... }}, 
          "metodologia": "Metodologia GERAL CONCISA.",
          "recursos_didaticos": "Recursos GERAIS CONCISOS.",
          "avaliacao": "Avaliação GERAL CONCISA."
        }}
        """

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)

        cleaned_response = response.text.strip().lstrip('```json').rstrip('```')

        try:
            parsed_json = json.loads(cleaned_response)
            # Validações básicas
            dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado"]
            if not all(isinstance(parsed_json.get(dia), dict) for dia in dias if
                       parsed_json.get(dia) is not None):  # Permite dias vazios (None ou ausente)
                raise ValueError("Estrutura JSON inválida: Chaves dos dias devem conter objetos.")
            for dia in dias:
                dia_data = parsed_json.get(dia)
                if dia_data is not None and not all(isinstance(val, str) for val in dia_data.values()):
                    raise ValueError(
                        f"Estrutura JSON inválida: Valores dentro do objeto do dia '{dia}' devem ser strings.")
            return parsed_json
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Erro ao processar JSON da IA: {e}")
            print(f"Resposta recebida: {cleaned_response}")
            return {
                "erro": f"A resposta da IA não é um JSON válido ou tem estrutura incorreta. {e}. Resposta: {cleaned_response}"}

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
        return {"erro": f"Ocorreu um erro na API: {e}"}