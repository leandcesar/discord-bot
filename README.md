<div align="center">
  <h1 align="center">discord-bot</h1>
  <p align="center">
    <a href="https://docs.python.org/3/"><img src="https://img.shields.io/badge/python 3-3776AB.svg?style=&logo=python&logoColor=white" alt="Python" href=""/></a>
    <a href="https://pre-commit.com/"><img src="https://img.shields.io/badge/pre--commit-FAB040.svg?style=&logo=pre-commit&logoColor=black" alt="precommit" /></a>
  </p>
</div>

---

## 🚀 Começando

### ✔️ Pré-requisitos

Antes de você começar, certifique-se que sua máquina tem os seguintes pré-requisitos instalados:
- Python>=3.10
- pip3

### ⤵️ Clonando

1. Clone o repositório para sua máquina local utilizando o [Git](https://git-scm.com/).
```sh
git clone git@github.com:leandcesar/discord-bot.git
```

### 💻 Instalando

2. Mude para o diretório do projeto.
```sh
cd discord-bot
```
3. Crie um [venv](https://docs.python.org/3/library/venv.html) e instale as dependências com [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/).
```sh
make install
```
4. Verifique se tudo foi instalado corretamente.
```sh
make version
```

### 🏃 Executar

4. Para executar localmente, primeiro preencha as variáveis de ambiente no arquivo `.env`.

5. Execute o bot do Discord.
```sh
make run
```

### 🧑‍💻 Desenvolvendo

6. Inicialize o [Gitflow](https://www.atlassian.com/br/git/tutorials/comparing-workflows/gitflow-workflow).
```sh
git flow init
```
7. Crie uma nova branch com um nome descritivo (`git flow feature|bugfix|hotfix start awesome_branch_name`).
```sh
git flow feature start awesome_branch_name
```
8. Faça as implementações no código na nova branch.

### 🪄 Estilo, formatação e segurança

9. Analise o código estaticamente com [ruff](https://beta.ruff.rs/docs/) e valide a tipagem com [mypy](https://mypy-lang.org/).
```sh
make lint
```
10. Formate o código nos padrões definidos com [black](https://black.readthedocs.io/en/stable/) e organize com [isort](https://pycqa.github.io/isort/).
```sh
make format
```
11. Valide problemas de segurança do código com [bandit](https://bandit.readthedocs.io/en/latest/).
```sh
make security
```

### ⤴️ Publicando

12. Commit suas mudanças na sua branch local utilizando mensagens no padrão do [Conventional Commit](https://www.conventionalcommits.org/en/) (por exemplo `git commit -m "feat|fix|refactor|style|test|docs|chore(scope): mensagem de exemplo"`).
```sh
git commit -m 'feat(readme): mensagem de exemplo'
```
13. Dê o push das suas mudanças para o repositório remoto do [GitHub](https://github.com/).
```sh
git push origin feature/awesome_branch_name
```
14. Crie um novo Pull Request para a branch `develop` no reposítorio do projeto.

### 🧹 Limpando

15. Remova os arquivos temporários de cache e outros.
```sh
make clean
```
16. E, se necessário, desinstale todas as dependências instaladas no passo 3.
```sh
make uninstall
```

## 📒 Referência

- [disnake](https://docs.disnake.dev/en/stable/index.html)
- [pillow](https://pillow.readthedocs.io/en/stable/#)
