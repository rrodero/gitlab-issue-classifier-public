import json
from pathlib import Path
import random

# --- Configuração ---
SOURCE_FILE = Path(__file__).parent.parent / "data" / "ground_truth_cleaned.jsonl"
VALIDATION_FILE = Path(__file__).parent.parent / "data" / "validation_set.jsonl"
TEST_FILE = Path(__file__).parent.parent / "data" / "test_set.jsonl"
VALIDATION_SPLIT_RATIO = 0.8  # 80% para validação, 20% para teste
RANDOM_SEED = 42

def split_dataset():
    """
    Lê o ground_truth.jsonl, embaralha e divide em validation_set.jsonl e test_set.jsonl.
    """

    print(f"📄 Lendo o dataset de origem: {SOURCE_FILE}")
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            all_cases = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo de origem '{SOURCE_FILE}' não encontrado.")
        return
    
    if not all_cases:
        print("⚠️ Aviso: O arquivo de origem está vazio. Nenhum arquivo foi criado.")
        return
    
    random.seed(RANDOM_SEED)
    random.shuffle(all_cases)

    split_index = int(len(all_cases) * VALIDATION_SPLIT_RATIO)

    validation_cases = all_cases[:split_index]
    test_cases = all_cases[split_index:]

    # Salva o arquivo de validação
    with open(VALIDATION_FILE, 'w', encoding='utf-8') as f:
        for case in validation_cases:
            f.write(json.dumps(case, ensure_ascii=False) + '\n')
    print(f"✅ Arquivo de validação salvo com {len(validation_cases)} casos em: {VALIDATION_FILE}") #noqa E501

    # Salva o arquivo de teste
    with open(TEST_FILE, 'w', encoding='utf-8') as f:
        for case in test_cases:
            f.write(json.dumps(case, ensure_ascii=False) + '\n')
    print(f"✅ Arquivo de teste salvo com {len(test_cases)} casos em: {TEST_FILE}")


if __name__ == "__main__":
    split_dataset()