import os
import sqlite3
from datetime import datetime, timezone

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS edicoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT UNIQUE NOT NULL,
    titulo TEXT NOT NULL,
    assunto TEXT NOT NULL DEFAULT '',
    conteudo_html TEXT NOT NULL DEFAULT '',
    documento_completo INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'rascunho',
    criada_em TEXT NOT NULL,
    publicada_em TEXT,
    enviada_em TEXT
);
CREATE TABLE IF NOT EXISTS inscritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    token TEXT UNIQUE NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS envios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edicao_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    status TEXT NOT NULL,
    detalhe TEXT NOT NULL DEFAULT '',
    enviado_em TEXT NOT NULL
);
"""


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_db():
    if "db" not in g:
        caminho = current_app.config["DATABASE"]
        diretorio = os.path.dirname(caminho)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)
        g.db = sqlite3.connect(caminho)
        g.db.row_factory = sqlite3.Row
    return g.db


def fechar_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        get_db().executescript(SCHEMA)


def registrar_fechamento(app):
    app.teardown_appcontext(fechar_db)
