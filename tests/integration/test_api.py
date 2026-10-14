from fastapi.testclient import TestClient

from src.main import app

# Cria o cliente de teste globalmente. Ele será usado por todas as funções de teste.
client = TestClient(app)


def test_classify_issue_endpoint_success(mocker):
    """
    Testa o 'caminho feliz' do endpoint, mockando a lógica de negócio e as env vars.
    """
    # 1. Simula as variáveis de ambiente para que a app possa ser inicializada sem erro.
    mocker.patch.dict(
        "os.environ",
        {
            "LLM_API_BASE_URL": "https://api.groq.com/openai/v1",
            "LLM_API_KEY": "dummy_key_for_ci",
            "LLM_MODEL_NAME": "llama3-8b-8192",
        },
    )

    # 2. Mocka a função de negócio para isolar o teste na camada da API.
    mock_classify = mocker.patch(
        "src.main.classify_issue",
        return_value=("time:devops", "Raciocínio de teste da API"),
    )

    # 3. Prepara o payload e faz a requisição.
    test_payload = {
        "title": "Build a CI/CD pipeline",
        "description": "We need to automate the deployment process.",
    }
    response = client.post("/classify-issue", json=test_payload)

    # 4. Verifica os resultados.
    assert response.status_code == 200
    expected_response = {
        "suggested_label": "time:devops",
        "reasoning": "Raciocínio de teste da API",
    }
    assert response.json() == expected_response
    mock_classify.assert_called_once()


def test_classify_issue_endpoint_validation_error(mocker):
    """
    Testa o erro de validação.
    """
    mocker.patch.dict(
        "os.environ",
        {
            "LLM_API_BASE_URL": "https://api.groq.com/openai/v1",
            "LLM_API_KEY": "dummy_key_for_ci",
            "LLM_MODEL_NAME": "llama3-8b-8192",
        },
    )

    invalid_payload = {"description": "This is a description without a title."}
    response = client.post("/classify-issue", json=invalid_payload)
    assert response.status_code == 422
