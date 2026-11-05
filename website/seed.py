import os
import re

from db import agora, get_db


def _titulo_do_html(html):
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    if not m:
        return None
    titulo = re.sub(r"\s+", " ", m.group(1)).strip()
    titulo = re.split(r"\s+[|–—-]\s+", titulo)[0].strip()
    return titulo or None


def seed_from_publicacoes(app):
    diretorio = app.config.get("PUBLICACOES_DIR", "")
    if not diretorio or not os.path.isdir(diretorio):
        return 0
    inseridos = 0
    for nome in sorted(os.listdir(diretorio)):
        if not nome.lower().endswith(".html"):
            continue
        m = re.search(r"(\d+)", nome)
        numero = m.group(1).zfill(2) if m else re.sub(r"\D", "", nome) or nome
        caminho = os.path.join(diretorio, nome)
        with open(caminho, encoding="utf-8", errors="replace") as arq:
            html = arq.read()
        titulo = _titulo_do_html(html) or f"Edicao {numero}"
        assunto = f"Decifrando Dados — Edicao #{numero}: {titulo}"
        with app.app_context():
            existente = get_db().execute(
                "SELECT id FROM edicoes WHERE numero = ?", (numero,)
            ).fetchone()
            if existente:
                continue
            get_db().execute(
                "INSERT INTO edicoes (numero, titulo, assunto, conteudo_html, documento_completo, status, criada_em, publicada_em)"
                " VALUES (?, ?, ?, ?, 1, 'publicada', ?, ?)",
                (numero, titulo, assunto, html, agora(), agora()),
            )
            get_db().commit()
            inseridos += 1
    return inseridos
