# Agente Classificador de Issues do GitLab

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![CI Pipeline](https://github.com/rrodero/gitlab-issue-classifier/actions/workflows/ci.yml/badge.svg)](https://github.com/rrodero/gitlab-issue-classifier/actions/workflows/ci.yml)

Um agente de IA que utiliza um Large Language Model (LLM) para analisar e sugerir etiquetas de time para issues do GitLab, ajudando a automatizar o processo de triagem.

O agente é exposto como um serviço de API utilizando FastAPI, permitindo integrações fáceis, como por exemplo, através de webhooks do GitLab.

## ✨ Features

- **Classificação Inteligente:** Utiliza LLMs para interpretar o conteúdo de títulos e descrições de issues.
- **Raciocínio Transparente (Chain-of-Thought):** O agente fornece uma explicação de por que escolheu uma determinada etiqueta, facilitando a depuração e aumentando a confiança.
- **Programação Defensiva:** Lógica de retentativas (retry) e valor padrão (fallback) para lidar com respostas inesperadas do LLM.
- **Observabilidade Completa:** Integrado com [Langfuse](https://langfuse.com) para rastreamento detalhado de cada classificação, incluindo custos, latência e o processo de raciocínio.
- **API Robusta:** Construído com FastAPI, oferecendo um endpoint validado e documentação interativa automática.

## 🚀 Começando

### Pré-requisitos

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (instalado via `pip install uv`)

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/rrodero/gitlab-issue-classifier.git](https://github.com/rrodero/gitlab-issue-classifier.git)
    cd gitlab-issue-classifier
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    uv pip sync requirements.lock
    ```

4.  **Configure as variáveis de ambiente:**
    - Copie o arquivo de exemplo:
      ```bash
      cp .env.example .env
      ```
    - Edite o arquivo `.env` e preencha com suas chaves de API (Langfuse, OpenAI/Google, etc.).

### Como Usar

1.  **Inicie o servidor da API:**
    ```bash
    uvicorn src.main:app --reload
    ```

2.  **Acesse a documentação interativa** no seu navegador em `http://127.0.0.1:8000/docs`.

3.  **Envie uma requisição de classificação** usando `curl` ou a interface do `/docs`:
    ```bash
    curl -X 'POST' \
      '[http://127.0.0.1:8000/classify-issue](http://127.0.0.1:8000/classify-issue)' \
      -H 'Content-Type: application/json' \
      -d '{
      "title": "Erro no agendamento do wolf",
      "description": "Agendei um job para ser executado todas as segundas-feiras mas ele não roda."
    }'
    ```

## 🛠️ Tecnologias Utilizadas

- **Framework da API:** FastAPI
- **Observabilidade:** Langfuse
- **Gerenciador de Pacotes:** uv
- **Testes:** Pytest
- **Linting/Formatting:** Ruff