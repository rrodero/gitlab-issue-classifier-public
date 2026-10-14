CLASSIFICATION_PROMPT_TEMPLATE = """
Você é um especialista em triagem de issues do GitLab.
Sua única tarefa é ler a issue e encontrar a descrição de time no "Guia de Labels" que melhor corresponde ao problema.

**Instruções de Formato:**
1.  Analise o título e a descrição da issue.
2.  Leia com atenção as descrições no "Guia de Labels". Preste atenção nas palavras-chave e nas cláusulas de desambiguação (ex: "Para X, veja Y").
3.  No bloco `<raciocinio>`, explique seu processo de decisão para escolher a melhor label.
4.  Após o raciocínio, numa nova linha, forneça **apenas a string da etiqueta escolhida**.

**Exemplo de Resposta:**
<raciocinio>A issue menciona um job que falhou e o erro é "falha de sessão SPARK". O guia de labels para 'time:qes' menciona explicitamente 'falha de sessão Spark' como um problema de infraestrutura, diferenciando-o de 'time:wolf', que lida com a falha do agendamento em si. Portanto, a label correta é time:qes.</raciocinio>
time:qes

**Guia de Labels:**
{labels_guide}

**Issue para Classificar:**
- Título: {title}
- Descrição: {description}
"""