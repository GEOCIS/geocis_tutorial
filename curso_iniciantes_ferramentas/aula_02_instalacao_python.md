# Aula 2: Instalação do Python

[← Aula 1](aula_01_introducao_ambiente.md) · [Plano do curso](README.md) · [Aula 3 →](aula_03_vscode.md)

## Resumo do plano

**Objetivos:** instalar o Python e executar o primeiro programa.

**Conteúdo:**

- Download no site oficial python.org e instalação por sistema operacional. No Windows, marcar a opção **Add python.exe to PATH** durante a instalação.
- Alternativa: distribuições como Anaconda ou Miniconda, que já trazem bibliotecas científicas e um gerenciador de ambientes. Explicar vantagens e desvantagens para o aluno escolher um caminho único.
- Verificação da instalação: `python --version` (no Windows, também `py --version`; no macOS e Linux, `python3 --version`) e `pip --version`.
- O interpretador interativo e a execução de scripts `.py`.

**Prática:** criar o arquivo `ola.py` com `print("Olá, mundo!")` e executá-lo no terminal. Em seguida, calcular a média de uma lista de números.

**Problemas comuns:** comando `python` não reconhecido (PATH não configurado) e confusão entre `python` e `python3`.

## Material de aula

**Materiais:** instaladores do Python (python.org), computador com permissão de instalação.

### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas da aula 1.
- 10 a 25 min: o que é o Python, versões e opções de distribuição.
- 25 a 55 min: instalação guiada por sistema operacional.
- 55 a 70 min: verificação e primeiro script.
- 70 a 110 min: introdução à linguagem (variáveis, listas, laços, condicionais e funções).
- 110 a 120 min: resumo e entregável.

### Conteúdo

**Python.org ou Anaconda?** Para manter o curso simples, adotamos o Python do site oficial com `venv` para ambientes e `pip` para bibliotecas. Anaconda e Miniconda são alternativas que trazem muitas bibliotecas científicas e outro gerenciador de ambientes (`conda`), mas misturar os dois caminhos na mesma turma dificulta o suporte. Use uma versão atual e estável do Python 3.

### Instalação guiada

**Windows**

1. Baixar o instalador em python.org/downloads.
2. Na primeira tela, **marcar "Add python.exe to PATH"** (essencial) e escolher *Install Now*.
3. Ao final, fechar e abrir novamente o PowerShell, e testar.

**macOS**

1. Baixar o instalador em python.org/downloads e executá-lo. Uma alternativa para quem já usa o gerenciador Homebrew é `brew install python`.
2. Abrir um novo Terminal e testar com `python3`.

**Linux (Debian e Ubuntu)**

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

**Verificação (em todos os sistemas)**

```bash
python --version      # no macOS e Linux: python3 --version; no Windows também funciona: py --version
pip --version         # no macOS e Linux: pip3 --version
```

O resultado deve mostrar a versão instalada (por exemplo, `Python 3.x.y`).

### Primeiro script

Criar a pasta `meus_projetos/aula02`, e nela o arquivo `ola.py` com um editor de texto simples (o VS Code será visto na próxima aula):

```python
print("Olá, mundo!")
```

Executar no terminal, dentro da pasta:

```bash
python ola.py
```

### Introdução à linguagem

Apresentar cada bloco no interpretador interativo (`python` no terminal; sair com `exit()`) ou em um arquivo `.py`:

```python
# variáveis e tipos
nome = "Solo A"
argila = 35.5          # float (número decimal)
n_amostras = 12        # int (número inteiro)
print(nome, argila, n_amostras)
print(type(argila))

# listas e laços
teores = [12.0, 18.5, 25.0, 31.2]
soma = 0
for t in teores:
    soma = soma + t
media = soma / len(teores)
print("Média:", media)

# condicional
if media > 20:
    print("Teor médio alto")
else:
    print("Teor médio baixo")

# função
def celsius_para_fahrenheit(c):
    return c * 9 / 5 + 32

print(celsius_para_fahrenheit(25))
```

Conceitos a destacar: a indentação (4 espaços) define os blocos, o `#` inicia comentários, e o nome da variável deve ser descritivo.

### Exercícios

1. Escrever um programa que imprima a tabuada do 7.
2. Criar uma função `media(lista)` que retorne a média dos valores de uma lista e testá-la com os teores de argila `[22, 35, 41, 18]`.
3. Encontrar o maior valor de uma lista com um laço, sem usar a função `max`.

**Gabarito**

```python
# 1
for i in range(1, 11):
    print("7 x", i, "=", 7 * i)

# 2
def media(lista):
    return sum(lista) / len(lista)
print(media([22, 35, 41, 18]))     # 29.0

# 3
valores = [22, 35, 41, 18]
maior = valores[0]
for v in valores:
    if v > maior:
        maior = v
print(maior)                        # 41
```

### Problemas comuns

- **`python` não é reconhecido**: o PATH não foi configurado. Reinstalar marcando a opção, ou usar `py` (Windows) e `python3` (macOS e Linux).
- **Terminal aberto antes da instalação**: fechar e abrir novamente.
- **Erro de indentação**: misturar espaços e tabulações, ou alinhar mal o bloco.

### Entregável

Arquivo `ola.py` e arquivo `exercicios.py` com as três soluções, executados sem erro.
