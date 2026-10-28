# Aula 3: VS Code, instalação e uso

[← Aula 2](aula_02_instalacao_python.md) · [Plano do curso](README.md) · [Aula 4 →](aula_04_ambientes_virtuais_bibliotecas.md)

## Resumo do plano

**Objetivos:** instalar e configurar o editor para trabalhar com Python.

**Conteúdo:**

- Instalação do Visual Studio Code (code.visualstudio.com).
- Tour pela interface: explorador de arquivos, editor, painel lateral, terminal integrado, barra de status e paleta de comandos (`Ctrl+Shift+P`).
- Extensões essenciais: **Python**, **Pylance** e **Jupyter** (todas da Microsoft). Depois, **GitHub Copilot**, na aula 9.
- Abrir uma pasta como projeto, criar arquivos, escolher o interpretador Python (comando *Python: Select Interpreter*) e executar um script.
- Personalização básica: tema, tamanho de fonte, salvamento automático.

**Prática:** abrir a pasta `meus_projetos`, criar `calculadora.py` com funções simples e executá-lo pelo botão de execução e pelo terminal integrado.

## Material de aula

**Materiais:** instalador do VS Code (code.visualstudio.com), acesso à internet para baixar extensões.

### Roteiro (120 min)

- 0 a 10 min: revisão da aula 2 e dúvidas.
- 10 a 30 min: instalação do VS Code.
- 30 a 55 min: tour pela interface.
- 55 a 75 min: extensões e interpretador Python.
- 75 a 95 min: executar e depurar um script.
- 95 a 115 min: personalização e atalhos.
- 115 a 120 min: resumo e entregável.

### Conteúdo

O **Visual Studio Code** (VS Code) é um editor de código gratuito e leve, com recursos que se ampliam por extensões. É diferente do *Visual Studio*, outro programa. Para Python, ele oferece destaque de sintaxe, sugestões, execução, depuração, terminal integrado e suporte a notebooks.

### Instalação

1. Baixar o instalador do site oficial, na versão correspondente ao sistema operacional.
2. **Windows:** durante a instalação, marcar as opções de adicionar "Abrir com Code" ao menu de contexto e de adicionar ao PATH. **macOS:** arrastar o aplicativo para a pasta Aplicativos. **Linux:** instalar o pacote `.deb` ou `.rpm`, ou pelo gerenciador de pacotes.
3. Abrir o VS Code e, se solicitado, confiar nas pastas de trabalho próprias (*Workspace Trust*).

### Tour pela interface

Mostrar, com o programa aberto, cada região:

- **Barra de atividades** (à esquerda): Explorador, Pesquisa, Controle do código-fonte (Git), Executar e depurar, Extensões.
- **Explorador:** arquivos e pastas do projeto aberto.
- **Editor:** área central com abas.
- **Painel inferior:** terminal integrado, problemas, saída.
- **Barra de status:** interpretador Python, linha e coluna, ramo do Git.
- **Paleta de comandos** (`Ctrl+Shift+P`, ou `Cmd+Shift+P` no macOS): acesso a qualquer comando digitando o nome. É a ferramenta mais útil para quem está começando.

### Extensões essenciais

Abrir a visão de extensões (`Ctrl+Shift+X`), pesquisar e instalar (as três são publicadas pela Microsoft):

- **Python**: execução, depuração e seleção de interpretador.
- **Pylance**: análise do código, sugestões e verificação de erros.
- **Jupyter**: suporte a notebooks (usado na aula 5).

A extensão do **GitHub Copilot** fica para a aula 9. Explicar que extensões devem ser instaladas apenas de editores confiáveis (verificar o selo de publicador e o número de instalações).

### Prática guiada

1. **Abrir a pasta do projeto:** *File > Open Folder* e escolher `meus_projetos/aula03`.
2. **Criar o arquivo** `calculadora.py` pelo Explorador (ícone de novo arquivo).
3. **Selecionar o interpretador:** paleta de comandos, *Python: Select Interpreter*, e escolher a versão instalada na aula 2.
4. **Escrever o código:**

```python
def somar(a, b):
    return a + b

def dividir(a, b):
    if b == 0:
        return "Divisão por zero"
    return a / b

if __name__ == "__main__":
    print(somar(2, 3))
    print(dividir(10, 4))
    print(dividir(1, 0))
```

5. **Executar:** botão de execução (triângulo) no canto superior direito do editor, ou no terminal integrado (`` Ctrl+` ``, a tecla de acento grave) com `python calculadora.py`.
6. **Depurar:** clicar à esquerda do número de uma linha para criar um ponto de parada (*breakpoint*, bolinha vermelha), pressionar `F5` e usar os botões para executar linha a linha e observar as variáveis no painel lateral.

### Personalização e atalhos

Configurações em *File > Preferences > Settings* (ou `Ctrl+,`):

- **Auto Save**: salvamento automático após atraso.
- **Font Size** e tema de cores.
- **Formatação ao salvar**, se houver um formatador instalado.

Atalhos úteis (no macOS, trocar `Ctrl` por `Cmd`):

- `Ctrl+P`: abrir arquivo pelo nome.
- `Ctrl+S`: salvar.
- `Ctrl+/`: comentar ou descomentar linhas.
- `Alt+↑` e `Alt+↓`: mover a linha.
- `Ctrl+Z`: desfazer.
- `Ctrl+F`: localizar.

### Exercícios

1. Adicionar à calculadora as funções `subtrair` e `multiplicar` e testar as quatro operações.
2. Executar o código no botão de execução e no terminal integrado, e comparar.
3. **Depuração:** o código abaixo deveria calcular a média, mas há um erro. Usar o depurador para encontrá-lo.

```python
def media(valores):
    soma = 0
    for v in valores:
        soma = soma + v
    return soma / len(valores) + 1

print(media([10, 20, 30]))
```

**Gabarito:** o `+ 1` no retorno está incorreto. O resultado correto é 20.0.

### Problemas comuns

- **Extensão Python não encontra o interpretador:** usar *Python: Select Interpreter* e escolher o caminho correto.
- **Terminal abre com o interpretador errado:** abrir um novo terminal depois de selecionar o interpretador.
- **Código não executa ao clicar no botão:** verificar se o arquivo foi salvo com a extensão `.py`.

### Entregável

Pasta `aula03` com `calculadora.py` (quatro operações) e a correção da função `media`.
