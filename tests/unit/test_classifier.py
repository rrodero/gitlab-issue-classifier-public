from pathlib import Path

from openai import OpenAI

from src.agent.classifier import classify_issue, load_labels_guide, parse_llm_output

# Define o caminho para a nossa pasta de fixtures de teste
TEST_FIXTURES_PATH = Path(__file__).parent.parent / "fixtures"


def test_load_labels_guide_success():
    """
    Testa se o arquivo existe e é válido.
    """
    mock_file_path = TEST_FIXTURES_PATH / "mock_labels_guide.json"
    # Chama a função, injetando o caminho base de teste
    labels_str, valid_labels = load_labels_guide(mock_file_path)

    # Verifica se a lista de labels está correta
    assert valid_labels == ["test:label-a", "test:label-b"]

    # Verifica se a string contém partes esperadas (não precisa ser exata)
    assert '"name": "test:label-a"' in labels_str
    assert '"description": "Segunda label de teste."' in labels_str


def test_load_labels_guide_file_not_found():
    """
    Testa se o arquivo não existe.
    """
    # Chama a função com um nome de arquivo que não existe
    labels_str, valid_labels = load_labels_guide("arquivo_inexistente.json")

    # Verifica se a função retornou os valores de fallback
    assert labels_str == "[]"
    assert valid_labels == []


def test_parse_llm_output_success():
    """
    Testa a extração correta de raciocínio e label.
    """
    llm_response = """<raciocinio>
    A issue menciona automação de testes e qualidade de código, o que se alinha com o time de QA.
    </raciocinio>
    time:qa-team"""  # noqa: E501

    reasoning, label = parse_llm_output(llm_response)

    assert (
        reasoning
        == "A issue menciona automação de testes e qualidade de código, o que se alinha com o time de QA."  # noqa: E501
    )
    assert label == "time:qa-team"


def test_parse_llm_output_no_reasoning():
    """
    Testa o caso em que o LLM não fornece raciocínio (apenas a label).
    """
    llm_response = "time:backend"

    reasoning, label = parse_llm_output(llm_response)

    assert reasoning == ""  # Esperamos que o raciocínio seja uma string vazia
    assert label == "time:backend"


def test_parse_llm_output_malformed_reasoning():
    """
    Testa o caso em que o raciocínio está malformado (tags incompletas).
    """
    llm_response = """<raciocinio>
    Este é um raciocínio malformado
    time:frontend"""  # Falta a tag de fechamento </raciocinio>

    reasoning, label = parse_llm_output(llm_response)

    assert reasoning == ""  # O regex não deve encontrar a tag completa
    assert label == "time:frontend"


def test_parse_llm_output_extra_newlines():
    """
    Testa o caso com novas linhas extras na resposta do LLM.
    """
    llm_response = """
    <raciocinio>

    Raciocínio com muitas linhas.

    </raciocinio>


    time:devops

    """

    reasoning, label = parse_llm_output(llm_response)

    assert reasoning == "Raciocínio com muitas linhas."
    assert label == "time:devops"


def test_classify_issue_success_on_first_try(mocker):
    """
    Testa se a função retorna a label correta na primeira tentativa válida.
    """
    mocker.patch("src.agent.classifier.get_client")

    # 1. Simula a função 'load_labels_guide'
    # para retornar um conjunto conhecido de labels
    mocker.patch(
        "src.agent.classifier.load_labels_guide",
        return_value=("dummy_json", ["time:devops", "time:wolf"]),
    )

    # 2. Mockamos a chamada real ao LLM para isolar o teste
    mock_llm_completion = mocker.patch(
        "src.agent.classifier.get_llm_completion",
        return_value="<raciocinio>Raciocínio de teste</raciocinio>\ntime:devops",
    )

    mock_llm_client = mocker.MagicMock(spec=OpenAI)

    dummy_path = Path("dummy_file.json")
    # 3. Executa a função a ser testada
    label, reasoning = classify_issue({}, dummy_path, mock_llm_client)

    # 5. Verifica os resultados
    assert mock_llm_completion.call_count == 1
    assert label == "time:devops"
    assert reasoning == "Raciocínio de teste"


def test_classify_issue_success_on_second_try(mocker):
    """
    Testa se a função tenta novamente e tem sucesso na segunda tentativa.
    """
    mocker.patch("src.agent.classifier.get_client")
    mocker.patch(
        "src.agent.classifier.load_labels_guide",
        return_value=("dummy_json", ["time:devops", "time:wolf"]),
    )

    # Simulamos uma sequência de respostas do LLM
    mock_llm_completion = mocker.patch("src.agent.classifier.get_llm_completion")
    mock_llm_completion.side_effect = [
        "<raciocinio>Inválido</raciocinio>\nlabel_errada",
        "<raciocinio>Válido</raciocinio>\ntime:wolf",
    ]

    mock_llm_client = mocker.MagicMock(spec=OpenAI)
    dummy_path = Path("dummy_file.json")
    label, reasoning = classify_issue({}, dummy_path, mock_llm_client)

    assert mock_llm_completion.call_count == 2
    assert label == "time:wolf"


def test_classify_issue_failure_and_fallback(mocker):
    """
    Testa se a função retorna o FALLBACK_LABEL após todas as tentativas falharem.
    """
    mocker.patch("src.agent.classifier.get_client")
    mocker.patch(
        "src.agent.classifier.load_labels_guide",
        return_value=("dummy_json", ["time:devops", "time:wolf"]),
    )

    mock_llm_completion = mocker.patch(
        "src.agent.classifier.get_llm_completion",
        return_value="<raciocinio>Falha</raciocinio>\nlabel_muito_errada",
    )

    mock_llm_client = mocker.MagicMock(spec=OpenAI)

    dummy_path = Path("dummy_file.json")

    label, reasoning = classify_issue({}, dummy_path, mock_llm_client)

    from src.agent import classifier

    assert mock_llm_completion.call_count == classifier.MAX_RETRIES
    assert label == classifier.FALLBACK_LABEL


def test_classify_issue_fallback_on_empty_llm_response(mocker):
    """
    Testa se a função aciona o fallback quando o LLM retorna uma string vazia.
    Este é um teste de robustez para nosso guardrail.
    """
    mocker.patch("src.agent.classifier.get_client")
    mocker.patch(
        "src.agent.classifier.load_labels_guide",
        return_value=("dummy_json", ["time:devops", "time:wolf"]),
    )

    mock_llm_completion = mocker.patch(
        "src.agent.classifier.get_llm_completion",
        return_value="",  # Resposta vazia
    )

    mock_llm_client = mocker.MagicMock(spec=OpenAI)
    dummy_path = Path("dummy_file.json")

    label, reasoning = classify_issue({}, dummy_path, mock_llm_client)

    from src.agent import classifier

    assert mock_llm_completion.call_count == classifier.MAX_RETRIES
    assert label == classifier.FALLBACK_LABEL
