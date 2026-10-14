import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

from langfuse import get_client
from openai import OpenAI

from src.integrations.llm_client import get_llm_completion
from src.prompts.classification_prompt import CLASSIFICATION_PROMPT_TEMPLATE

# Constantes de configuração
MAX_RETRIES = 3
FALLBACK_LABEL = "time:atendimento"  # Direcionado para triagem humana


def load_labels_guide(file_path: Path) -> Tuple[str, List[str]]:
    """Carrega o guia de labels,
    retornando uma string formatada e uma lista de nomes de label."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            labels_data: List[Dict[str, str]] = json.load(f)

        # Extrai apenas os nomes das labels para a validação
        valid_labels = [item["name"] for item in labels_data]

        # Formata o JSON completo como string para o prompt
        labels_guide_str = json.dumps(labels_data, indent=2, ensure_ascii=False)

        return labels_guide_str, valid_labels
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(
            f"Erro crítico ao carregar ou processar o guia de labels '{file_path}': {e}"
        )
        # Retorna valores seguros em caso de erro
        return "[]", []


def parse_llm_output(response: str) -> Tuple[str, str]:
    """Extrai o raciocínio e a label da saída do LLM."""
    reasoning = ""
    label = ""

    try:
        reasoning_match = re.search(r"\*\*Raciocínio:\*\*(.*?)\*\*Resposta Final:\*\*", response, re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        else:
            # Fallback para o método antigo com tags XML, para retrocompatibilidade
            reasoning_match_xml = re.search(r"<raciocinio>(.*?)</raciocinio>", response, re.DOTALL)
            if reasoning_match_xml:
                reasoning = reasoning_match_xml.group(1).strip()

        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        if lines:
            last_line = lines[-1]
            if "time:" in last_line:
                label = last_line[last_line.find("time:"):]
            else:
                label = last_line
    except Exception as e:
        print(f"Erro ao analisar a saída do LLM: {e}")
        # Em caso de erro de parsing, retorna a resposta bruta como label para depuração
        return "", response


    return reasoning, label


def classify_issue(
    issue_data: dict, labels_guide_path: Path, llm_client: OpenAI
) -> Tuple[str, str]:
    """Classifica uma issue do GitLab com lógica de validação, retry e fallback."""
    langfuse = get_client()

    # Span PAI: representa toda a operação de classificação.
    with langfuse.start_as_current_span(name="issue-classification") as parent_span:
        # Span FILHO 1: representa apenas o carregamento do arquivo.
        with langfuse.start_as_current_span(name="load-labels-guide") as load_span:
            labels_guide, valid_labels = load_labels_guide(labels_guide_path)
            load_span.update(output={"valid_labels_count": len(valid_labels)})

        if not valid_labels:
            error_reason = "Nenhuma label válida carregada, usando fallback."
            parent_span.update(output={"error": error_reason})
            return FALLBACK_LABEL, error_reason

        parent_span.update(input=issue_data)

        prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(
            labels_guide=labels_guide,
            title=issue_data.get("title", ""),
            description=issue_data.get("description", ""),
        )

        for attempt in range(MAX_RETRIES):
            with langfuse.start_as_current_observation(
                name=f"llm-classification-attempt-{attempt + 1}",
                as_type="generation",
                model=os.getenv("LLM_MODEL_NAME", "llama3"),
                input=prompt,
            ) as generation:
                print(f"Tentativa {attempt + 1}/{MAX_RETRIES}: Chamando o LLM real...")
                llm_output_raw = get_llm_completion(prompt, llm_client)
                reasoning, label = parse_llm_output(llm_output_raw)

                generation.update(
                    output={
                        "raw": llm_output_raw,
                        "reasoning": reasoning,
                        "label": label,
                    }
                )

                # -- VALIDACAO --
                if label in valid_labels:
                    print(f"Saída '{label}' é válida. Sucesso!")
                    parent_span.update(output=label)
                    return label, reasoning
                else:
                    print(f"Saída '{label}' é INVÁLIDA. Tentando novamente...")

        # -- FALLBACK --
        err_message = f"Todas as {MAX_RETRIES} tentativas falharam. Usando o fallback."
        print(err_message)

        parent_span.update(
            output=FALLBACK_LABEL,
            level="ERROR",
            status_message=err_message,
        )
        return FALLBACK_LABEL, "Falha na classificação após múltiplas tentativas."
