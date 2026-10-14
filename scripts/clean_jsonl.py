import json
from pathlib import Path

# --- Configuração ---
SOURCE_FILE = Path(__file__).parent.parent / "data" / "ground_truth.jsonl"
CLEANED_FILE = Path(__file__).parent.parent / "data" / "ground_truth_cleaned.jsonl"

def clean_jsonl():
    """
    Lê um arquivo .jsonl que pode conter JSONs malformados (com múltiplas linhas)
    e o reescreve em um formato .jsonl válido, com um JSON por linha.
    """
    print(f"🧹 Limpando o arquivo: {SOURCE_FILE}")
    
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            # Lê o conteúdo inteiro, pois os JSONs podem abranger várias linhas
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo de origem '{SOURCE_FILE}' não encontrado.")
        return

    # Tenta analisar o conteúdo como uma sequência de objetos JSON
    try:
        # Usa um decoder para ler múltiplos objetos JSON de uma string
        decoder = json.JSONDecoder()
        pos = 0
        all_cases = []
        while pos < len(content.strip()):
            obj, pos = decoder.raw_decode(content, pos)
            all_cases.append(obj)
            # Avança para o próximo caractere não-espaço em branco
            pos = content.find('{', pos)
            if pos == -1: # Se não houver mais '{', termina
                break
    except json.JSONDecodeError as e:
        print(f"❌ Erro de formatação JSON no arquivo de origem: {e}")
        print("   O script não conseguiu corrigir o arquivo automaticamente.")
        print("   Por favor, verifique se há erros de sintaxe JSON (ex: vírgulas faltando).")
        return

    # Salva o novo arquivo, garantindo um JSON por linha
    with open(CLEANED_FILE, 'w', encoding='utf-8') as f:
        for case in all_cases:
            # O dumps garante que caracteres especiais como quebras de linha sejam escapados
            f.write(json.dumps(case, ensure_ascii=False) + '\n')
            
    print(f"✅ Arquivo limpo salvo com {len(all_cases)} casos em: {CLEANED_FILE}")
    print("\nPróximo passo: renomeie 'ground_truth_cleaned.jsonl' para 'ground_truth.jsonl' e execute o script 'split_dataset.py' novamente.")

if __name__ == "__main__":
    clean_jsonl()