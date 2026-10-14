# Guia de Desenvolvimento

Bem-vindo ao guia de desenvolvimento do Agente Classificador de Issues! Este documento descreve como configurar seu ambiente para contribuir com o projeto.

## ⚙️ Configurando o Ambiente de Desenvolvimento

O processo é semelhante à instalação padrão, com um passo adicional para instalar as dependências de desenvolvimento (`pytest`, `ruff`, etc.).

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

3.  **Instale todas as dependências (incluindo as de desenvolvimento):**
    ```bash
    uv pip sync requirements.lock
    uv pip install -e ".[dev]"
    ```

4.  **Configure as variáveis de ambiente:**
    - Copie o arquivo de exemplo: `cp .env.example .env`
    - Preencha o `.env` com suas chaves.

## ✅ Executando os Testes

Nós usamos `pytest` para os testes de unidade e integração. A automação desses testes é garantida por uma pipeline no GitHub Actions.

Para executar a suíte de testes localmente, a partir da raiz do projeto, use o comando:
```bash
pytest