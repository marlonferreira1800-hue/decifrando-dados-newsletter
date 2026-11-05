# 🌐 Website da Newsletter Decifrando Dados

Site oficial da newsletter: página pública com arquivo de edições, formulário de
inscrição, e painel do editor para **criar, editar, publicar e enviar** as edições
por e-mail para os inscritos.

## Estrutura

```
website/
├── app.py            # Rotas públicas e do admin (Flask)
├── db.py             # Schema SQLite e helpers de banco
├── mailer.py         # Envio por SMTP (env) ou log local
├── seed.py           # Importa edições HTML de ../publicacoes para o banco
├── requirements.txt
├── templates/        # Páginas públicas e do admin
├── static/           # CSS e JS do editor
└── tests/            # Testes de fumaça (unittest)
```

## Como rodar localmente

```bash
cd website
pip install -r requirements.txt
ADMIN_PASSWORD=sua-senha python app.py
```

Abra <http://127.0.0.1:5000>. Na primeira execução, as edições existentes em
`../publicacoes/*.html` são importadas automaticamente para o arquivo do site
(guardadas em `website/newsletter.db`, que não vai para o git).

Atalhos prontos: no Windows, dois cliques em `run.bat`; no Linux/Mac, `./run.sh`.

## Não está abrindo? Solução de problemas

- **`python` não é reconhecido / abre a Microsoft Store** → instale o Python 3.10+
  em <https://python.org> marcando **"Add Python to PATH"** na instalação.
- **`ModuleNotFoundError: No module named 'flask'`** → rode
  `pip install -r requirements.txt` (ou use `run.bat` / `run.sh`, que instalam as dependências sozinhos).
- **Rode a partir da pasta certa** — `python app.py` funciona dentro de `website/`
  (ou `python website/app.py` a partir da raiz do repositório não funciona; use os atalhos).
- **Abra a URL certa no navegador**: <http://127.0.0.1:5000> (não abra o arquivo HTML direto).
- **Porta 5000 ocupada** → `PORT=8000 python app.py` e abra <http://127.0.0.1:8000>.
- **A janela do servidor fechou** → não feche a janela preta do terminal; é ela que mantém o site no ar.

## Variáveis de ambiente

| Variável | Padrão | Descrição |
| :--- | :--- | :--- |
| `SECRET_KEY` | `dev-secret-change-me` | Troque em produção. |
| `ADMIN_PASSWORD` | `admin123` | Senha do painel `/admin`. **Troque sempre.** |
| `DATABASE` | `website/newsletter.db` | Caminho do banco SQLite. |
| `SITE_NAME` | `Decifrando Dados` | Nome exibido no site. |
| `SITE_TAGLINE` | `Smart people are cooler.` | Tagline do hero. |
| `SMTP_HOST` | *(vazio)* | Se definido, envia e-mails de verdade via SMTP. |
| `SMTP_PORT` | `587` | Porta do SMTP. |
| `SMTP_USER` / `SMTP_PASSWORD` | *(vazio)* | Credenciais SMTP (use variáveis de ambiente, nunca commite). |
| `SMTP_FROM` | remetente do `SMTP_USER` | Remetente do e-mail. |
| `SMTP_TLS` | `1` | `0` desativa STARTTLS. |
| `PORT` | `5000` | Porta do servidor local. |

Sem `SMTP_HOST`, os envios são registrados no console e na tabela `envios`
(modo log — útil para testar sem enviar e-mail de verdade).

## Fluxo do editor

1. `/admin/login` com a senha de administrador.
2. **+ Nova edição** → informe número, título, assunto do e-mail e escreva o
   conteúdo no editor visual (negrito, títulos, listas, links) com prévia ao vivo.
3. **Publicar** → a edição entra no ar em `/edicao/<id>` e no arquivo `/edicoes`.
4. **Enviar** → escolha "todos" (todos os inscritos ativos, com link de
   descadastro individual) ou "teste" (um e-mail seu). O histórico fica em
   **Envios**.
5. **Inscritos** lista os e-mails ativos; cada um pode se remover pelo link de
   descadastro no rodapé do e-mail (`/descadastrar/<token>`).

## Testes

```bash
cd website
python -m unittest discover -s tests -v
```

## Segurança

- Senha do admin comparada em tempo constante; sessão assinada com `SECRET_KEY`.
- Formulários do admin e de descadastro protegidos por token CSRF.
- Edições antigas (HTML completo) são exibidas em iframe com `sandbox` e `srcdoc`.
- Credenciais SMTP apenas via variáveis de ambiente — nunca no código.
