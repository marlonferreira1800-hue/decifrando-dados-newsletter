# 📰 Decifrando Dados — Hub de Produção & Publicação Oficial

Repositório oficial de produção, automação, compilação e publicação da newsletter **Decifrando Dados**, com curadoria e autoria de **Marlon Ferreira**.

- **URL Oficial no LinkedIn:** [linkedin.com/newsletters/decifrando-dados-7513791689808064512](https://www.linkedin.com/newsletters/decifrando-dados-7513791689808064512/)
- **Missão:** Desmistificar Ciência de Dados, Machine Learning, Engenharia de Dados e Inteligência Artificial para profissionais de TI, Setor Bancário/Financeiro e Negócios/Público Geral sem parecer acadêmico demais, com foco em impacto prático real e sem enrolação.
- **Slogan Oficial:** *"Smart people are cooler."*

---

## 🎯 Sistema de Conteúdo em Duas Etapas (Novo Modelo Oficial)

Com uma única pauta, o sistema produz automaticamente duas peças complementares:

1. **Etapa 1 — A Newsletter Completa (Leitura de 3 a 4 minutos):**
   - **Cabeçalho & 3 Tópicos Âncora:** Foco na transformação prática do mercado.
   - **Bloco 1 — O Ponto Central:** Gancho corporativo real + explicação sem "tecniquês" + callout de **Analogia Simples do Cotidiano** (*"Em outras palavras..."*).
   - **Bloco 2 — Na Prática (As 3 Lentes):**
     - 💻 **TI e Tecnologia:** Arquitetura, governança, segurança cibernética e times técnicos.
     - 🏦 **Setor Bancário e Financeiro:** Prevenção a fraudes, risco de crédito, compliance e auditoria.
     - 📊 **Negócios e Público Geral:** Tomada de decisão, rotina de trabalho e custos.
   - **Bloco 3 — Tradutor de IA & Dados:** 1 termo técnico por edição (O que parece ser, O que realmente é, Por que você vai ouvir falar).
   - **Bloco 4 — Radar Rápido da Semana:** 2 notícias ou tendências + 1 ferramenta ou caso prático.
   - **Bloco 5 — Para Levar para a Semana:** Pergunta reflexiva prática + assinatura oficial.

2. **Etapa 2 — O Post para o Feed do LinkedIn (Leitura de 45 a 60 segundos):**
   - Gancho de alto impacto nas primeiras 2 linhas para clique em *"...ver mais"*.
   - Resumo direto do fato + analogia condensada em 1 frase.
   - O que significa na prática para as 3 áreas (**TI e Dados**, **Bancos e Finanças**, **Negócios**).
   - Conceito-chave da semana em 1 linha.
   - Pergunta de engajamento para comentários.
   - Link para ler a newsletter completa no primeiro comentário + hashtags estratégicas.

---

## ⚡ Executáveis Rápidos (1-Clique no Windows)

| Executável | Função Principal |
| :--- | :--- |
| **`CENTRAL_NEWSLETTER.bat`** | 🎛️ **Painel Central:** Menu interativo para acessar todas as operações da newsletter. |
| **`1_INICIAR_REDACAO_VIRTUAL.bat`** | 🏢 **Redação Virtual 2D:** Inicia o servidor local (`:8080`) com IA (NVIDIA NIM) e feed de notícias. |
| **`2_COMPILAR_EDICAO_PDF.bat`** | 📄 **Compilador Oficial:** Compila o Markdown para PDF diagramado, HTML responsivo e copia o pacote LinkedIn. |
| **`3_CRIAR_NOVA_EDICAO_IA.bat`** | 🤖 **Criador Autônomo com IA:** Basta fornecer link ou tema para disparar os agentes seguindo a *Receita de Bolo*. |
| **`4_COPIAR_ARTIGO_LINKEDIN.bat`** | 📋 **Copiador LinkedIn (Ctrl+V):** Copia instantaneamente SEO, Post do Feed e Artigo Completo para a Área de Transferência. |
| **`5_ABRIR_PASTA_PDFS.bat`** | 📁 **Pasta de Saída:** Atalho direto para visualizar os PDFs compilados. |

---

## 📁 Estrutura do Repositório

```text
01_Newsletter_Decifrando_Dados/
├── 📄 CENTRAL_NEWSLETTER.bat            <- Painel Central Interativo
├── 📄 1_INICIAR_REDACAO_VIRTUAL.bat     <- Inicia a Redação Virtual 2D
├── 📄 2_COMPILAR_EDICAO_PDF.bat         <- Compila Edições para PDF/HTML/LinkedIn
├── 📄 3_CRIAR_NOVA_EDICAO_IA.bat        <- Criador Autônomo com IA
├── 📄 4_COPIAR_ARTIGO_LINKEDIN.bat      <- Copia Pacote LinkedIn para Clipboard
├── 📄 5_ABRIR_PASTA_PDFS.bat            <- Atalho para os PDFs compilados
├── 📄 RECEITA_DE_BOLO_NEWSLETTER.md     <- Guia e Modelo Oficial Rigoroso (5 Blocos)
├── 📄 README.md                         <- Documentação do projeto
├── 📄 .gitignore                        <- Exclusões de ambiente, ROMs e binários temporários
│
├── 📂 edicoes/                          <- Fonte Oficial (.md, .pdf, .html, .txt)
│   ├── edicao_01.md                     <- Edição #01 atualizada no novo modelo oficial
│   ├── edicao_01.html                   <- HTML responsivo com toolbar de 1 clique
│   ├── edicao_01.pdf                    <- PDF diagramado em alta resolução
│   └── edicao_01_artigo_linkedin.txt    <- Pacote completo (SEO + Post + Artigo)
│
├── 📂 publicacoes/                      <- Histórico e compilações de edições
│
├── 📂 Gerador de Newsletter/            <- Scripts compiladores oficiais
│   ├── build_newsletter.py              <- Compilador oficial (Markdown -> PDF/HTML/TXT)
│   ├── criar_newsletter.py              <- Disparador de novas edições
│   ├── compilar_interativo.py           <- Menu interativo de compilação
│   ├── copiar_linkedin.py               <- Utilitário de injeção no Clipboard (Ctrl+V)
│   └── template.html                    <- Layout base visual moderno
│
└── 📂 redacao-virtual/                  <- Motor da Redação Virtual 2D
    ├── server.py                        <- Backend aiohttp assíncrono com suporte a .env
    ├── .env.example                     <- Exemplo de variáveis de ambiente
    └── public/                          <- Frontend RPG 2D Canvas
```

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem Principal:** Python 3.10+
- **Compilação de PDFs:** Microsoft Edge Headless (diagramação A4 vetorial)
- **Frontend Interativo:** HTML5 Canvas, Tailwind CSS, Lucide Icons, Glassmorphism
- **Modelos de IA:** NVIDIA NIM (Nemotron 550B, Gemma 31B), Google Gemini Pro
- **Integração:** Clipboard API do Windows, LinkedIn Article & Feed Publisher
