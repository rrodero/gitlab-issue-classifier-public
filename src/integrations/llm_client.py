import os

from openai import OpenAI


def get_llm_completion(prompt: str, client: OpenAI) -> str:
    """
    Envia um prompt para o endpoint do LLM configurado e retorna a resposta.
    O cliente OpenAI é passado como um argumento.
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL_NAME", "llama3"),
            messages=[
                {"role": "system", "content": "Você é um assistente prestativo."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,  # Usamos 0 para máxima consistência na classificação
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar a API do LLM: {e}")
        return ""  # Retorna uma string vazia em caso de erro
