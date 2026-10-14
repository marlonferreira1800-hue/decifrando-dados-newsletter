"""
Iniciador Autônomo de Newsletter 'Decifrando Dados' (Guia Oficial em Duas Etapas) via AGY
Desenvolvido para Marlon Ferreira.
Salva todas as gerações (.md, .pdf, .html, _artigo_linkedin.txt) em:
C:\\Users\\marlo\\OneDrive\\Desktop\\Pasta Projetos\\01_Newsletter_Decifrando_Dados\\edicoes
"""

import sys
import os
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AGY_PATH = r"C:\Users\marlo\AppData\Local\agy\bin\agy.exe"
EDICOES_DIR = r"C:\Users\marlo\OneDrive\Desktop\Pasta Projetos\01_Newsletter_Decifrando_Dados\edicoes"
BUILD_SCRIPT = r"C:\Users\marlo\OneDrive\Desktop\Pasta Projetos\01_Newsletter_Decifrando_Dados\Gerador de Newsletter\build_newsletter.py"

BANNER = r"""
==============================================================================
  📰 DECIFRANDO DADOS  •  GERADOR 100% AUTÔNOMO (MODELO EM DUAS ETAPAS)
==============================================================================
  Curadoria: Marlon Ferreira  •  Slogan: Smart people are cooler
  Destino Oficial: 01_Newsletter_Decifrando_Dados\edicoes
==============================================================================
"""

def main():
    print(BANNER)
    print(" Insira a pauta da sua nova edição.")
    print(" Pode ser um LINK de notícia, caminho de ARQUIVO ou apenas o TEMA:\n")
    
    try:
        entrada = input(" 🎯 Cole aqui o Link / Arquivo / Tema: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nOperação cancelada.")
        return

    if not entrada:
        print("\n❌ Nenhuma entrada informada. Encerrando.")
        return

    print("\n" + "─" * 78)
    print(f" 🚀 Iniciando o AGY em Modo Autônomo com o Guia Oficial em Duas Etapas...")
    print("─" * 78 + "\n")

    super_prompt = (
        f'Crie a nova edição completa da newsletter oficial Decifrando Dados seguindo estritamente '
        f'a RECEITA_DE_BOLO_NEWSLETTER.md e o "Guia e Modelos de Publicação: Newsletter & LinkedIn" com base neste link/arquivo/tema: "{entrada}".\n\n'
        f'REGRAS OBRIGATÓRIAS DO MODELO EM DUAS ETAPAS:\n'
        f'1. ESTRUTURA EM DUAS ETAPAS:\n'
        f'   - Etapa 1: Newsletter Completa (leitura de 3-4 minutos) em 5 Blocos estruturados.\n'
        f'   - Etapa 2: Post de Divulgação para o LinkedIn (leitura de 45-60 segundos) com gancho e adaptação nas 3 áreas.\n'
        f'2. AS 3 LENTES PRÁTICAS OBRIGATÓRIAS: Toda análise deve detalhar o impacto nas 3 frentes:\n'
        f'   • Para Tecnologia e Dados (TI): arquitetura, integração, governança, segurança, código.\n'
        f'   • Para o Setor Bancário e Financeiro: prevenção a fraudes, risco, crédito, compliance, auditoria, custos.\n'
        f'   • Para Negócios e Público Geral: gestão, tomadores de decisão, dia a dia, assinaturas/orçamento.\n'
        f'3. ANALOGIA DO COTIDIANO: Bloco 1 deve conter "> 💡 **Em outras palavras (A Analogia):** Pense nisso como..." comparando o conceito a uma cena simples do dia a dia.\n'
        f'4. TRADUTOR DE IA & DADOS: Explique 1 termo técnico da pauta em 3 linhas estruturadas:\n'
        f'   • O que parece ser: [frase leve descontraída]\n'
        f'   • O que realmente é: [explicação direta em até 2 frases]\n'
        f'   • Por que você vai ouvir falar disso: [onde aparece no mercado]\n'
        f'5. RADAR RÁPIDO DA SEMANA: 2 notícias curtas + 1 ferramenta/caso prático de 2 linhas cada.\n'
        f'6. PARA LEVAR PARA A SEMANA: "> 🎯 **A pergunta prática da edição:**" reflexiva + assinatura com convite para compartilhar.\n'
        f'7. GUIA DE BOLSO DE TRADUÇÃO DE "TECNIQUÊS": Foco no problema real e valor prático, evitando fórmulas soltas e jargões acadêmicos.\n'
        f'8. FRONTMATTER YAML: titulo, subtitulo, assunto, categoria, edicao, data, dia_semana, tempo_leitura, seo_titulo, seo_descricao e post_divulgacao completo para o feed do LinkedIn.\n'
        f'9. PASTA OFICIAL DE GERAÇÃO: Descubra o próximo número de edição em "{EDICOES_DIR}", salve o arquivo .md gerado em "{EDICOES_DIR}" e compile imediatamente executando:\n'
        f'   python "{BUILD_SCRIPT}" --input "{EDICOES_DIR}\\edicao_XX.md" --output-dir "{EDICOES_DIR}" --pdf --copy\n'
        f'   gerando o PDF, o HTML e o arquivo _artigo_linkedin.txt todos dentro de "{EDICOES_DIR}" e copiando pro Clipboard.\n'
        f'10. Execute tudo de forma 100% autônoma até a entrega final completa.'
    )

    cmd = [
        AGY_PATH,
        "--dangerously-skip-permissions",
        "-i",
        super_prompt
    ]

    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"\n❌ Erro ao disparar o AGY: {e}")

if __name__ == "__main__":
    main()
