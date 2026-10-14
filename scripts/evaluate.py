import httpx
import json
from pathlib import Path
import random
import argparse
from datetime import datetime
import time
import asyncio
import traceback

# --- Configuração ---
API_URL = "http://127.0.0.1:8000/classify-issue"
DEFAULT_GOLDEN_SET_PATH = Path(__file__).parent.parent / "data" / "ground_truth.jsonl"
RESULTS_DIR = Path(__file__).parent.parent / "evaluation_reports"
MAX_CONCURRENCY = 5  # Número de requisições paralelas. Ajuste conforme a capacidade do seu servidor.
REQUEST_TIMEOUT = 300.0 # Tempo de espera em segundos para cada requisição

def format_duration(seconds: float) -> str:
    """Converte segundos em um formato legível (horas, minutos, segundos)."""
    if seconds < 60:
        return f"{seconds:.2f} segundos"
    
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{int(hours)} hora(s)")
    if minutes > 0:
        parts.append(f"{int(minutes)} minuto(s)")
    if seconds > 0:
        parts.append(f"{seconds:.2f} segundo(s)")
        
    return ", ".join(parts)

async def evaluate_case(client: httpx.AsyncClient, case: dict, case_num: int, total_cases: int) -> dict:
    """Função assíncrona para avaliar um único caso."""
    input_data = case["input"]
    expected_label = case["expected_output"]
    
    print(f"  - Testando caso {case_num}/{total_cases}: '{input_data['title']}'...")

    try:
        response = await client.post(API_URL, json=input_data, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        response_data = response.json()
        predicted_label = response_data.get("suggested_label")

        if predicted_label == expected_label:
            return {"correct": True}
        else:
            return {
                "correct": False,
                "error_details": {
                    "case": case_num,
                    "input": input_data,
                    "expected": expected_label,
                    "predicted": predicted_label,
                    "reasoning": response_data.get("reasoning", "N/A")
                }
            }
    except httpx.RequestError as e:
        error_message = f"Erro de Conexão no caso #{case_num}: {e.__class__.__name__} - {e}"
        print(f"  ❌ {error_message}")
        return {
            "correct": False, 
            "error_details": { "case": case_num, "input": input_data, "expected": expected_label, "predicted": f"FALHA: {e.__class__.__name__}" }
        }
    except Exception as e:
        error_message = f"Erro Inesperado no caso #{case_num}"
        print(f"  ❌ {error_message}")
        traceback.print_exc() # Imprime o stack trace completo do erro
        return {
            "correct": False, 
            "error_details": { "case": case_num, "input": input_data, "expected": expected_label, "predicted": "FALHA: Erro Inesperado" }
        }
    
    return {
        "correct": False, 
        "error_details": {
            "case": case_num, 
            "input": input_data, 
            "expected": expected_label, 
            "predicted": "ERRO DE EXECUÇÃO"
        }
    }

async def run_evaluation(file_path: Path, sample_size: int | None):
    """Executa a avaliação de forma assíncrona."""
    start_time = time.time()
    
    print(f"🚀 Iniciando avaliação do agente usando o arquivo: {file_path.name}")
    RESULTS_DIR.mkdir(exist_ok=True)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_test_cases = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo de avaliação não encontrado em '{file_path}'")
        return

    if not all_test_cases:
        print("⚠️ Aviso: O arquivo de avaliação está vazio.")
        return

    if sample_size and len(all_test_cases) > sample_size:
        print(f"Selecionando uma amostra aleatória de {sample_size} de {len(all_test_cases)} casos...")
        test_cases = random.sample(all_test_cases, sample_size)
    else:
        test_cases = all_test_cases
    
    correct_predictions = 0
    errors = []
    
    async with httpx.AsyncClient() as client:
        semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
        
        async def run_with_semaphore(case, i):
            async with semaphore:
                return await evaluate_case(client, case, i + 1, len(test_cases))

        tasks = [run_with_semaphore(case, i) for i, case in enumerate(test_cases)]
        results = await asyncio.gather(*tasks)

    for result in results:
        if result and result.get("correct"):
            correct_predictions += 1
        elif result and "error_details" in result:
            errors.append(result["error_details"])
    
    end_time = time.time()
    duration = end_time - start_time
    formatted_duration = format_duration(duration)

    report_lines = []
    report_lines.append("--- ✅ Relatório de Avaliação Concluído ---")
    
    total_cases = len(test_cases)
    accuracy = (correct_predictions / total_cases) * 100 if total_cases > 0 else 0
    
    report_lines.append(f"\nArquivo Avaliado: {file_path.name}")
    report_lines.append(f"Tamanho da Amostra: {total_cases}")
    report_lines.append(f"Tempo de Duração: {formatted_duration}")
    report_lines.append(f"Previsões Corretas: {correct_predictions}")
    report_lines.append(f"Acurácia: {accuracy:.2f}%")

    if errors:
        errors.sort(key=lambda x: x['case']) # Ordena os erros por número do caso
        report_lines.append("\n--- 🔍 Análise dos Erros ---")
        for error in errors:
            report_lines.append(f"\nCaso #{error['case']}: '{error['input']['title']}'")
            report_lines.append(f"  - Esperado:   '{error['expected']}'")
            report_lines.append(f"  - Obtido:     '{error['predicted']}'")
            report_lines.append(f"  - Raciocínio do LLM: \"{error.get('reasoning', 'N/A')}\"")
    
    report_lines.append("\n-------------------------------------------")

    report_content = "\n".join(report_lines)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"evaluation_report_{timestamp}.txt"
    report_path = RESULTS_DIR / report_filename

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(report_content)
    print(f"\n📄 Relatório salvo em: {report_path}")

def main():
    """Função principal para analisar argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description="Script de Avaliação do Agente Classificador.")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_GOLDEN_SET_PATH,
        help=f"Caminho para o arquivo .jsonl de avaliação. Padrão: {DEFAULT_GOLDEN_SET_PATH}"
    )
    parser.add_argument(
        "--sample_size",
        type=int,
        default=None,
        help="Número de casos a serem amostrados. Deixe em branco para rodar em todos os casos."
    )
    args = parser.parse_args()
    
    sample_size = args.sample_size if args.sample_size is not None and args.sample_size > 0 else None
    
    # Executa a função principal com asyncio
    asyncio.run(run_evaluation(args.file, sample_size))

if __name__ == "__main__":
    main()