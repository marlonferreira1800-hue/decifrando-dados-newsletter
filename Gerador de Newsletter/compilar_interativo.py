#!/usr/bin/env python3
"""
Compilador Interativo de Edições - Decifrando Dados
Lê e salva todas as gerações (Markdown, PDF, HTML e LinkedIn) em:
C:\\Users\\marlo\\OneDrive\\Desktop\\Pasta Projetos\\01_Newsletter_Decifrando_Dados\\edicoes
"""

import os
import re
import sys
import subprocess
from pathlib import Path

EDICOES_DIR = Path(r"C:\Users\marlo\OneDrive\Desktop\Pasta Projetos\01_Newsletter_Decifrando_Dados\edicoes")
PUBLICACOES_DIR = EDICOES_DIR
BUILD_SCRIPT = Path(__file__).resolve().parent / "build_newsletter.py"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def get_edition_info(md_path: Path):
    """Extrai número e título do frontmatter de uma edição."""
    titulo = md_path.stem
    edicao = ""
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("titulo:"):
                    titulo = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("edicao:"):
                    edicao = line.split(":", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return edicao, titulo


def list_editions():
    """Retorna a lista ordenada de arquivos .md em edicoes/."""
    EDICOES_DIR.mkdir(parents=True, exist_ok=True)
    files = list(EDICOES_DIR.glob("*.md"))
    def sort_key(p):
        match = re.search(r"(\d+)", p.stem)
        return int(match.group(1)) if match else 9999
    files.sort(key=sort_key)
    return files


def run_compiler(md_file: Path):
    """Executa o build_newsletter.py com PDF e cópia para Clipboard."""
    print(f"\n⚙️ Compilando: {md_file.name} ...")
    cmd = [
        sys.executable,
        str(BUILD_SCRIPT),
        "--input", str(md_file),
        "--output-dir", str(EDICOES_DIR),
        "--pdf",
        "--copy"
    ]
    res = subprocess.run(cmd)
    if res.returncode == 0:
        pdf_path = EDICOES_DIR / f"{md_file.stem}.pdf"
        print(f"✅ Sucesso! PDF gerado em: {pdf_path}")
        return pdf_path
    else:
        print(f"❌ Falha ao compilar {md_file.name}")
        return None


def main():
    print("=" * 78)
    print("  📰 DECIFRANDO DADOS  •  COMPILADOR OFICIAL DE EDIÇÕES (MODELO EM DUAS ETAPAS)")
    print("=" * 78)
    print(f"  Pasta Oficial (MD, PDF, HTML e LinkedIn): {EDICOES_DIR}")
    print("=" * 78 + "\n")

    files = list_editions()
    if not files:
        print("❌ Nenhuma edição encontrada em", EDICOES_DIR)
        input("\nPressione ENTER para voltar...")
        return

    print("Edições disponíveis:\n")
    for idx, f in enumerate(files, 1):
        ed_num, title = get_edition_info(f)
        print(f"  [{idx:02d}] {f.name:<38} | {title[:36]}")

    print("\n" + "─" * 78)
    escolha = input("🎯 Digite o NÚMERO (1-{}) ou termo (ex: 37, ou 'todas'): ".format(len(files))).strip()

    if not escolha:
        print("Operação cancelada.")
        return

    to_compile = []
    if escolha.lower() in ("todas", "all", "*"):
        to_compile = files
    elif escolha.isdigit() and 1 <= int(escolha) <= len(files):
        to_compile = [files[int(escolha) - 1]]
    else:
        matched = [f for f in files if escolha.lower() in f.stem.lower()]
        if matched:
            to_compile = matched
        else:
            print(f"❌ Nenhuma edição encontrada correspondente a '{escolha}'.")
            input("\nPressione ENTER para voltar...")
            return

    last_pdf = None
    for f in to_compile:
        pdf = run_compiler(f)
        if pdf and pdf.exists():
            last_pdf = pdf

    if last_pdf and last_pdf.exists():
        print("\n" + "─" * 78)
        print(f"📋 Artigo do LinkedIn copiado para a Área de Transferência (Ctrl+V)!")
        resp = input(f"🔍 Deseja abrir o PDF '{last_pdf.name}' agora? [S/N]: ").strip().lower()
        if resp in ("s", "sim", "y", "yes"):
            try:
                os.startfile(str(last_pdf))
            except Exception as e:
                print(f"Aviso: Não foi possível abrir o PDF: {e}")

    print("\nConcluído com sucesso!")
    input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
