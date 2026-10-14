#!/usr/bin/env python3
"""
Copiador de Artigo do LinkedIn - Decifrando Dados
Lê o pacote completo direto de:
C:\\Users\\marlo\\OneDrive\\Desktop\\Pasta Projetos\\01_Newsletter_Decifrando_Dados\\edicoes
"""

import os
import re
import sys
import subprocess
import webbrowser
from pathlib import Path

EDICOES_DIR = Path(r"C:\Users\marlo\OneDrive\Desktop\Pasta Projetos\01_Newsletter_Decifrando_Dados\edicoes")
LINKEDIN_URL = "https://www.linkedin.com/newsletters/decifrando-dados-7513791689808064512/"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def copy_to_clipboard(text: str) -> bool:
    try:
        import ctypes
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        user32.OpenClipboard.argtypes = [ctypes.c_void_p]
        user32.OpenClipboard.restype = ctypes.c_int
        user32.EmptyClipboard.argtypes = []
        user32.EmptyClipboard.restype = ctypes.c_int
        user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        user32.SetClipboardData.restype = ctypes.c_void_p
        user32.CloseClipboard.argtypes = []
        user32.CloseClipboard.restype = ctypes.c_int
        kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalUnlock.restype = ctypes.c_int

        encoded = text.encode("utf-16-le") + b"\x00\x00"
        h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
        if not h_mem:
            return False
        ptr = kernel32.GlobalLock(h_mem)
        if not ptr:
            return False
        ctypes.memmove(ptr, encoded, len(encoded))
        kernel32.GlobalUnlock(h_mem)
        if not user32.OpenClipboard(None):
            return False
        user32.EmptyClipboard()
        user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        user32.CloseClipboard()
        return True
    except Exception as e:
        print(f"Erro ao copiar: {e}")
        return False


def list_linkedin_articles():
    EDICOES_DIR.mkdir(parents=True, exist_ok=True)
    files = list(EDICOES_DIR.glob("*_artigo_linkedin.txt"))
    def sort_key(p):
        match = re.search(r"(\d+)", p.stem)
        return int(match.group(1)) if match else 9999
    files.sort(key=sort_key)
    return files


def main():
    print("=" * 78)
    print("  📋 DECIFRANDO DADOS  •  COPIAR PACOTE DO LINKEDIN (CTRL+V)")
    print("=" * 78)
    print(f"  Pasta: {EDICOES_DIR}")
    print("=" * 78 + "\n")

    files = list_linkedin_articles()
    if not files:
        print("❌ Nenhum arquivo de artigo do LinkedIn encontrado em", EDICOES_DIR)
        print("💡 Dica: Compile uma edição primeiro usando o '2_COMPILAR_EDICAO_PDF.bat'.")
        input("\nPressione ENTER para voltar...")
        return

    print("Artigos prontos para o LinkedIn:\n")
    for idx, f in enumerate(files, 1):
        clean_name = f.stem.replace("_artigo_linkedin", "")
        print(f"  [{idx:02d}] {clean_name}")

    print("\n" + "─" * 78)
    escolha = input(f"🎯 Digite o NÚMERO (1-{len(files)}) ou parte do nome (ex: 37): ").strip()

    if not escolha:
        print("Operação cancelada.")
        return

    selected = None
    if escolha.isdigit() and 1 <= int(escolha) <= len(files):
        selected = files[int(escolha) - 1]
    else:
        for f in files:
            if escolha.lower() in f.stem.lower():
                selected = f
                break

    if not selected:
        print(f"❌ Nenhuma edição encontrada para '{escolha}'.")
        input("\nPressione ENTER para voltar...")
        return

    with open(selected, "r", encoding="utf-8") as f:
        content = f.read()

    if copy_to_clipboard(content):
        print("\n" + "═" * 78)
        print("  🎉 PACOTE DO LINKEDIN COPIADO COM SUCESSO!")
        print("═" * 78)
        print(f"  Arquivo: {selected.name}")
        print("  Conteúdo enviado para a Área de Transferência (Ctrl+V):")
        print("   ✅ Metadados de SEO para o LinkedIn (Título e Descrição)")
        print("   ✅ Post de Divulgação com Gancho e Hashtags")
        print("   ✅ Artigo Completo Formatado (DNA The BRIEF)")
        print("═" * 78 + "\n")

        resp = input("🌐 Deseja abrir a página da Newsletter no LinkedIn agora? [S/N]: ").strip().lower()
        if resp in ("s", "sim", "y", "yes"):
            webbrowser.open(LINKEDIN_URL)
    else:
        print("❌ Falha ao copiar para a área de transferência.")

    print("\nPronto! Basta colar (Ctrl+V) no LinkedIn.")
    input("Pressione ENTER para continuar...")


if __name__ == "__main__":
    main()
