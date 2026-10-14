import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from langfuse import get_client
from openai import OpenAI

from src.agent.classifier import classify_issue
from src.agent.models import ClassificationResponse, IssuePayload

# Carrega as variáveis de ambiente na inicialização
load_dotenv()

app = FastAPI(
    title="Agente Classificador de Issues",
    description="Uma API para sugerir labels para issues do GitLab usando um LLM.",
    version="0.1.0",
)


def get_llm_client():
    """Esta função cria e retorna um cliente OpenAI."""
    return OpenAI(
        base_url=os.getenv("LLM_API_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
    )


# Inicializa o cliente Langfuse globalmente para a aplicação
langfuse_client = get_client()


@app.post("/classify-issue", response_model=ClassificationResponse)
def classify_issue_endpoint(
    payload: IssuePayload, llm_client: OpenAI = Depends(get_llm_client)
):
    """
    Recebe os dados de uma issue e retorna uma sugestão de label e o raciocínio.
    """
    # Constrói o caminho para o arquivo de labels de produção
    # labels_file_path = Path(__file__).parent.parent / "data" / "big_labels_time.json"
    labels_file_path = Path(__file__).parent.parent / "data" / "labels_guide_v2.json"

    issue_data = payload.model_dump()

    suggested_label, reasoning = classify_issue(
        issue_data=issue_data, labels_guide_path=labels_file_path, llm_client=llm_client
    )

    langfuse_client.flush()

    return ClassificationResponse(suggested_label=suggested_label, reasoning=reasoning)
