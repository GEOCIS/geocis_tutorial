# Aula 4: Ambientes virtuais e bibliotecas

[← Aula 3](aula_03_vscode.md) · [Plano do curso](README.md) · [Aula 5 →](aula_05_jupyter_notebook.md)

## Resumo do plano

**Objetivos:** entender por que isolar projetos e instalar bibliotecas com segurança.

**Conteúdo:**

- O que são bibliotecas e o que o `pip` faz.
- Ambiente virtual: o problema de misturar versões entre projetos e a solução com `venv`.
  - Criar: `python -m venv .venv`
  - Ativar no Windows: `.venv\Scripts\activate`; no macOS e Linux: `source .venv/bin/activate`
- Instalar bibliotecas: `pip install pandas numpy matplotlib scipy scikit-learn ipykernel`
- Listar e registrar dependências: `pip list` e `pip freeze > requirements.txt`; reinstalar em outro computador com `pip install -r requirements.txt`.
- Papel de cada biblioteca: **numpy** (matrizes), **pandas** (tabelas), **matplotlib** (gráficos), **scipy** (cálculo científico) e **scikit-learn** (aprendizado de máquina).

**Prática:** criar o ambiente virtual do projeto, selecioná-lo no VS Code e instalar as bibliotecas. Testar com `import pandas as pd` e imprimir `pd.__version__`.

**Problemas comuns:** PowerShell bloqueando a ativação do ambiente (política de execução de scripts) e instalação feita fora do ambiente virtual.

## Material de aula

**Materiais:** VS Code configurado, acesso à internet para instalar pacotes.

### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 30 min: o que são bibliotecas e ambientes virtuais.
- 30 a 60 min: criar e ativar o ambiente.
- 60 a 80 min: instalar e registrar bibliotecas.
- 80 a 110 min: teste das bibliotecas na prática.
- 110 a 120 min: resumo e entregável.

### Conteúdo

**Bibliotecas** são conjuntos de código prontos para tarefas específicas. O `pip` é o programa que baixa e instala bibliotecas do repositório público PyPI.

**Por que ambientes virtuais?** Cada projeto pode precisar de versões diferentes das mesmas bibliotecas. Sem isolamento, atualizar uma biblioteca para um projeto pode quebrar outro. Um ambiente virtual é uma pasta com uma cópia isolada do Python e das bibliotecas instaladas apenas para aquele projeto. Isso também torna o projeto reprodutível, pois a lista de bibliotecas pode ser registrada e reinstalada em outro computador.

**As bibliotecas do curso:**

- **numpy**: matrizes e operações numéricas rápidas.
- **pandas**: tabelas (DataFrames) para leitura, limpeza e análise de dados.
- **matplotlib**: gráficos.
- **scipy**: funções científicas (estatística, filtros, otimização).
- **scikit-learn**: aprendizado de máquina e estatística.
- **ipykernel**: permite que o VS Code execute notebooks com o ambiente.

### Prática guiada

**1. Criar o ambiente** (dentro da pasta do projeto `meus_projetos/aula04`, no terminal integrado do VS Code):

```bash
python -m venv .venv
```

(No macOS e Linux, use `python3` se `python` não existir.)

**2. Ativar o ambiente:**

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Prompt de Comando)
.venv\Scripts\activate.bat

# macOS e Linux
source .venv/bin/activate
```

Com o ambiente ativo, o início da linha do terminal passa a mostrar `(.venv)`. Para sair do ambiente: `deactivate`.

**Atenção (Windows):** se o PowerShell bloquear a ativação por política de execução de scripts, uma solução é executar `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e confirmar. Explique ao aluno o que esse comando altera, e prefira o Prompt de Comando se não quiser mudar a política.

**3. Selecionar o ambiente no VS Code:** paleta de comandos, *Python: Select Interpreter*, e escolher o que aparece com `.venv`. O VS Code costuma sugerir isso automaticamente ao detectar a pasta `.venv`.

**4. Instalar as bibliotecas:**

```bash
python -m pip install --upgrade pip
pip install numpy pandas matplotlib scipy scikit-learn ipykernel
```

**5. Conferir e registrar:**

```bash
pip list                      # lista o que está instalado
pip freeze > requirements.txt # registra versões
```

Para reinstalar tudo em outro computador ou ambiente: `pip install -r requirements.txt`.

**6. Testar as bibliotecas** com o arquivo `teste_bibliotecas.py`:

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

print("numpy:", np.__version__)
print("pandas:", pd.__version__)

# numpy: operações com vetores
x = np.linspace(0, 10, 50)
y = np.sin(x)
print("Média de y:", y.mean())

# pandas: uma tabela pequena
df = pd.DataFrame({"amostra": ["A", "B", "C"], "argila": [22.0, 35.5, 41.0]})
print(df)
print(df["argila"].mean())

# matplotlib: um gráfico
plt.plot(x, y)
plt.title("Seno")
plt.savefig("seno.png")
print("Gráfico salvo em seno.png")
```

### Exercícios

1. Criar um segundo ambiente (`.venv2`), instalar apenas o numpy e verificar com `pip list` que as outras bibliotecas não estão presentes. Explicar o que isso demonstra.
2. Gerar o `requirements.txt` do primeiro ambiente e usá-lo para recriar um ambiente novo em outra pasta.
3. Usar o numpy para criar um vetor de 100 valores aleatórios (`np.random.default_rng(0).normal(0, 1, 100)`) e calcular média e desvio-padrão.

### Problemas comuns

- **A biblioteca foi instalada, mas o `import` falha:** o terminal ou o VS Code estão usando outro Python. Conferir o `(.venv)` no terminal e o interpretador selecionado.
- **`pip` não é reconhecido:** usar `python -m pip install ...`.
- **Erro de permissão ao instalar:** conferir se o ambiente virtual está ativo e evitar instalar com `sudo` ou como administrador.
- **Instalação lenta ou com falha de rede:** repetir o comando e verificar a conexão.

### Entregável

Pasta `aula04` com o ambiente `.venv`, o arquivo `requirements.txt`, o `teste_bibliotecas.py` funcionando e o gráfico `seno.png`.
