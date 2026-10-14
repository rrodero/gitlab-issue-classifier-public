# Agente Classificador de Issues do GitLab — Pacote de Replicação (SBQS 2026)

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![CI Pipeline](https://github.com/rrodero/gitlab-issue-classifier-public/actions/workflows/ci.yml/badge.svg)](https://github.com/rrodero/gitlab-issue-classifier-public/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Este repositório contém o artefacto de software, os conjuntos de dados anonimizados e os scripts de avaliação experimental associados ao artigo aceite no **XXV Simpósio Brasileiro de Qualidade de Software (SBQS 2026)**.

---

## 📌 Descrição Geral do Artefacto

O artefacto consiste num agente inteligente baseado em Large Language Model (LLM) desenhado para analisar títulos e descrições de issues do GitLab e sugerir etiquetas (*labels*) de equipa, automatizando o processo de triagem. O sistema é disponibilizado como um serviço de API REST construído com FastAPI e inclui os pipelines de pré-processamento, divisão de dados e avaliação empírica reportados no estudo.

### Funcionalidades Principais
- **Classificação Automatizada:** Interpretação semântica de títulos e descrições de issues via LLM.
- **Raciocínio Transparente (*Chain-of-Thought*):** Geração de justificações estruturadas para cada etiqueta atribuída, facilitando a auditoria e depuração.
- **Programação Defensiva:** Mecanismos de repetição (*retry*) e valores padrão (*fallback*) para lidar com respostas fora do formato esperado.
- **Observabilidade:** Integração com [Langfuse](https://langfuse.com) para rastreamento de execuções, latência, custos e prompts.
- **Serviço de API:** Endpoint validado com FastAPI e documentação interativa automática (OpenAPI/Swagger).

---

## 📄 Artigo Relacionado

- **Título:** Observability-Guided Verification and Validation of LLM Agents: An Exploratory Case Study
- **Autores:** Rafael Henrique Rodero, Diges Feltrin Guizelini e Elaine Venson
- **Evento:** XXV Simpósio Brasileiro de Qualidade de Software (SBQS 2026)
- **Link para o Artigo (Versão do Autor):** [Inserir URL para o PDF da versão do autor]
- **Depósito Persistente (Zenodo DOI):** `https://doi.org/10.5281/zenodo.XXXXXXX`

---

## 📂 Organização do Repositório

A estrutura de diretórios e ficheiros do projeto está organizada da seguinte forma:

```text
├── .env.example                   # Modelo das variáveis de ambiente necessárias
├── .github/workflows/ci.yml       # Pipeline de Integração Contínua (GitHub Actions)
├── .python-version                # Especificação da versão do Python (3.13)
├── DEVELOPMENT.md                 # Documentação técnica complementar de desenvolvimento
├── LICENSE                        # Licença de distribuição do artefacto (MIT)
├── README.md                      # Documentação principal do pacote de replicação
├── pyproject.toml                 # Definição do projeto, metadados e dependências
├── requirements.lock              # Versões fixadas de todos os pacotes para reprodutibilidade
├── data/                          # Conjuntos de dados e guias de etiquetas utilizados no estudo
│   ├── big_labels_time.json       # Mapeamento de etiquetas de equipas
│   ├── ground_truth.jsonl         # Conjunto de dados base (anonimizado)
│   ├── ground_truth_cleaned.jsonl # Conjunto de dados higienizado após pré-processamento
│   ├── labels_guide_v2.json       # Guia base com descrições das etiquetas
│   ├── labels_guide_enriched.json # Guia de descrições das etiquetas enriquecido
│   ├── test_set.jsonl             # Partição de teste utilizada na avaliação experimental
│   └── validation_set.jsonl       # Partição de validação utilizada na calibração
├── scripts/                       # Scripts para reprodução do fluxo experimental
│   ├── clean_jsonl.py             # Higienização e normalização dos ficheiros JSONL
│   ├── split_dataset.py           # Divisão dos dados em conjuntos de validação e teste
│   └── evaluate.py                # Execução da avaliação experimental e cálculo de métricas
├── src/                           # Código-fonte do agente classificador e da API
│   ├── main.py                    # Ponto de entrada da aplicação FastAPI
│   ├── agent/
│   │   ├── classifier.py          # Lógica central de classificação do agente
│   │   └── models.py              # Esquemas de dados e validação (Pydantic)
│   ├── integrations/
│   │   └── llm_client.py          # Cliente de integração com a API do LLM
│   └── prompts/
│       └── classification_prompt.py # Templates de prompt utilizados pelo classificador
└── tests/                         # Suíte de testes automatizados (Pytest)
    ├── conftest.py                # Configurações e fixtures globais de teste
    ├── fixtures/
    │   └── mock_labels_guide.json # Dados simulados para execução de testes isolados
    ├── unit/
    │   └── test_classifier.py     # Testes unitários da lógica do classificador
    ├── integration/
    │   └── test_api.py            # Testes de integração dos endpoints da API
    └── behavioral/
        └── test_consistency.py    # Testes comportamentais e de consistência de respostas
```

---

## 📊 Conjunto de Dados: Armazenamento e Considerações Éticas

- **Formato e Armazenamento:** Os conjuntos de dados encontram-se no diretório `data/` nos formatos JSON (`.json`) para os dicionários/guias de etiquetas e JSON Lines (`.jsonl`) para os registos das issues. Este formato permite inspeção direta e processamento em *streaming* sem necessidade de sistemas de gestão de bases de dados externos.
- **Considerações Éticas e Anonimização:** Todos os dados contidos em `data/` foram submetidos a um processo de anonimização e expurgo antes da publicação. Dados pessoais identificáveis (PII), nomes de utilizadores, referências de infraestrutura interna, URLs privadas e credenciais foram removidos ou substituídos por identificadores genéricos, garantindo a proteção de dados e a conformidade ética.

---

## 💻 Requisitos de Sistema

- **Sistema Operativo:** Linux, macOS ou Windows (recomendado via WSL2).
- **Hardware Mínimo:** Processador Dual-Core, 4 GB de memória RAM, 1 GB de espaço livre em disco e ligação ativa à Internet (para comunicação com a API do modelo de linguagem).
- **Ambiente de Software:**
  - Python `3.13` (definido em `.python-version`)
  - Gestor de pacotes e ambientes [uv](https://github.com/astral-sh/uv)
- **Credenciais Externas:** Chave de API válida do fornecedor de LLM (configurada via ficheiro `.env`). As chaves do Langfuse são opcionais para rastreamento de telemetria.

---

## 🚀 Instalação e Configuração (Passo a Passo)

1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/rrodero/gitlab-issue-classifier-public.git](https://github.com/rrodero/gitlab-issue-classifier-public.git)
   cd gitlab-issue-classifier-public
   ```

2. **Instalar o gestor de pacotes `uv` (caso não esteja instalado):**
   ```bash
   pip install uv
   ```

3. **Criar e ativar o ambiente virtual com Python 3.13:**
   ```bash
   uv venv --python 3.13
   source .venv/bin/activate
   ```
   *(No Windows PowerShell, utilize: `.venv\Scripts\Activate.ps1`)*

4. **Instalar as dependências com versões fixadas (`requirements.lock`):**
   ```bash
   uv pip sync requirements.lock
   ```

5. **Configurar as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   ```
   Abra o ficheiro `.env` num editor de texto e preencha as variáveis com as suas credenciais de API (fornecedor de LLM e, opcionalmente, Langfuse).

---

## 🔬 Instruções de Execução e Reprodução dos Experimentos

### 1. Executar a Suíte de Testes Automatizados
Para verificar a integridade da instalação e validar os testes unitários, de integração e comportamentais sem custo de chamadas reais (utilizando mocks quando aplicável):
```bash
pytest
```

### 2. Reproduzir o Pré-processamento e Divisão do Conjunto de Dados
Os ficheiros processados (`ground_truth_cleaned.jsonl`, `validation_set.jsonl` e `test_set.jsonl`) já estão incluídos na pasta `data/`. Caso deseje executar novamente o pipeline de preparação de dados:
```bash
# 1. Higienização do dataset bruto
python scripts/clean_jsonl.py

# 2. Divisão em conjuntos de validação e teste
python scripts/split_dataset.py
```

### 3. Executar a Avaliação Experimental
Para executar o agente classificador sobre o conjunto de dados e reproduzir as métricas reportadas no artigo:
```bash
python scripts/evaluate.py
```

---

## 🌐 Execução do Serviço de API (Demonstração Interativa)

Para iniciar o agente como um serviço web local e testar classificações individuais:

1. **Iniciar o servidor FastAPI:**
   ```bash
   uvicorn src.main:app --reload
   ```

2. **Aceder à documentação interativa:**
   Abra o navegador em `http://127.0.0.1:8000/docs` para visualizar a interface Swagger UI.

3. **Testar o endpoint de classificação via linha de comandos (`curl`):**
   ```bash
   curl -X 'POST' \
     '[http://127.0.0.1:8000/classify-issue](http://127.0.0.1:8000/classify-issue)' \
     -H 'Content-Type: application/json' \
     -d '{
     "title": "Erro no agendamento do job",
     "description": "Agendei um job para ser executado todas as segundas-feiras mas ele não roda."
   }'
   ```

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.13
- **Framework Web:** FastAPI / Uvicorn
- **Observabilidade de LLM:** Langfuse
- **Gestão de Dependências:** uv
- **Testes Automatizados:** Pytest
- **Análise Estática e Formatação:** Ruff

---

## 📜 Licença

Este projeto é distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para obter os termos completos de utilização, modificação e distribuição.