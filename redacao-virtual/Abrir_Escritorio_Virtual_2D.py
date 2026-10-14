"""
Lançador Nativo Python (Imune a falso-positivo de antivírus em arquivos .bat)
Inicia o servidor da Redação Virtual 2D na porta 8080 e abre o navegador automaticamente.
Basta dar 2 cliques neste arquivo!
"""
import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

PORT = 8080
URL = f"http://localhost:{PORT}"
SERVER_SCRIPT = Path(__file__).resolve().parent / "server.py"


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    if not is_port_in_use(PORT):
        creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        subprocess.Popen(
            [sys.executable, str(SERVER_SCRIPT), str(PORT)],
            cwd=str(SERVER_SCRIPT.parent),
            creationflags=creation_flags,
        )
        for _ in range(20):
            if is_port_in_use(PORT):
                break
            time.sleep(0.25)

    webbrowser.open(URL)


if __name__ == "__main__":
    main()
