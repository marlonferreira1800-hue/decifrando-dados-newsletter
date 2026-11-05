import hmac
import os
import re
import secrets
from functools import wraps

from flask import (
    Flask,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from db import agora, get_db, init_db, registrar_fechamento
from mailer import get_mailer

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD", "admin123"),
        DATABASE=os.path.join(app.root_path, "newsletter.db"),
        PUBLICACOES_DIR=os.path.abspath(os.path.join(app.root_path, "..", "publicacoes")),
        SEED_ON_INIT=True,
        SITE_NAME=os.environ.get("SITE_NAME", "Decifrando Dados"),
        SITE_TAGLINE=os.environ.get("SITE_TAGLINE", "Smart people are cooler."),
        MAILER=None,
    )
    if test_config:
        app.config.update(test_config)

    init_db(app)
    registrar_fechamento(app)

    if app.config.get("SEED_ON_INIT"):
        from seed import seed_from_publicacoes

        seed_from_publicacoes(app)

    app.jinja_env.globals["csrf_token"] = csrf_token

    registrar_routes(app)
    return app


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


def check_csrf():
    enviado = request.form.get("_csrf", "")
    return bool(enviado) and hmac.compare_digest(session.get("_csrf", ""), enviado)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped


def mailer_atual():
    return current_app.config.get("MAILER") or get_mailer()


def buscar_edicao(edicao_id):
    return get_db().execute("SELECT * FROM edicoes WHERE id = ?", (edicao_id,)).fetchone()


def montar_email_html(edicao, token, base_url):
    conteudo = edicao["conteudo_html"]
    if edicao["documento_completo"]:
        m = re.search(r"<body[^>]*>(.*)</body>", conteudo, re.S | re.I)
        if m:
            conteudo = m.group(1)
    link_descadastro = (
        f'<p style="text-align:center;margin-top:32px;">'
        f'<a href="{base_url}/descadastrar/{token}" style="color:#6b7280;font-size:12px;">'
        f"Descadastrar deste e-mail</a></p>"
        if token
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:24px;background:#f3f4f6;font-family:Arial,Helvetica,sans-serif;">
<div style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;">
<div style="background:#0f172a;color:#f8fafc;padding:20px 28px;">
  <div style="font-size:18px;font-weight:bold;">Decifrando Dados</div>
  <div style="font-size:12px;color:#94a3b8;">Edição #{edicao['numero']} — Smart people are cooler.</div>
</div>
<div style="padding:28px;">{conteudo}</div>
<div style="background:#f9fafb;padding:16px 28px;font-size:12px;color:#6b7280;text-align:center;">
  Você recebe este e-mail porque se inscreveu na newsletter Decifrando Dados.
  {link_descadastro}
</div>
</div></body></html>"""


def registrar_routes(app):
    @app.get("/")
    def index():
        db = get_db()
        recentes = db.execute(
            "SELECT id, numero, titulo, publicada_em FROM edicoes WHERE status = 'publicada'"
            " ORDER BY CAST(numero AS INTEGER) DESC LIMIT 3"
        ).fetchall()
        total = db.execute(
            "SELECT COUNT(*) AS c FROM edicoes WHERE status = 'publicada'"
        ).fetchone()["c"]
        inscritos = db.execute(
            "SELECT COUNT(*) AS c FROM inscritos WHERE ativo = 1"
        ).fetchone()["c"]
        return render_template(
            "index.html", recentes=recentes, total_edicoes=total, total_inscritos=inscritos
        )

    @app.get("/edicoes")
    def edicoes():
        lista = get_db().execute(
            "SELECT id, numero, titulo, publicada_em FROM edicoes WHERE status = 'publicada'"
            " ORDER BY CAST(numero AS INTEGER) DESC"
        ).fetchall()
        return render_template("edicoes.html", edicoes=lista)

    @app.get("/edicao/<int:edicao_id>")
    def ver_edicao(edicao_id):
        edicao = buscar_edicao(edicao_id)
        if not edicao or edicao["status"] != "publicada":
            abort(404)
        return render_template("edicao.html", edicao=edicao)

    @app.post("/inscrever-se")
    def inscrever_se():
        email = request.form.get("email", "").strip().lower()
        if not EMAIL_RE.match(email):
            flash("Informe um e-mail válido.", "erro")
            return redirect(url_for("index") + "#inscricao")
        db = get_db()
        existente = db.execute(
            "SELECT id, ativo FROM inscritos WHERE email = ?", (email,)
        ).fetchone()
        if existente:
            if not existente["ativo"]:
                db.execute(
                    "UPDATE inscritos SET ativo = 1 WHERE id = ?", (existente["id"],)
                )
                db.commit()
                flash("Sua inscrição foi reativada. Bem-vindo de volta!", "ok")
            else:
                flash("Este e-mail já está inscrito.", "info")
        else:
            db.execute(
                "INSERT INTO inscritos (email, token, ativo, criado_em) VALUES (?, ?, 1, ?)",
                (email, secrets.token_urlsafe(24), agora()),
            )
            db.commit()
            flash("Inscrição confirmada! Você receberá as próximas edições.", "ok")
        return redirect(url_for("index") + "#inscricao")

    @app.get("/descadastrar/<token>")
    def descadastrar(token):
        inscrito = get_db().execute(
            "SELECT * FROM inscritos WHERE token = ?", (token,)
        ).fetchone()
        if not inscrito:
            abort(404)
        return render_template("descadastrar.html", inscrito=inscrito, token=token)

    @app.post("/descadastrar/<token>")
    def descadastrar_confirma(token):
        if not check_csrf():
            abort(400)
        db = get_db()
        inscrito = db.execute(
            "SELECT id FROM inscritos WHERE token = ?", (token,)
        ).fetchone()
        if not inscrito:
            abort(404)
        db.execute("UPDATE inscritos SET ativo = 0 WHERE id = ?", (inscrito["id"],))
        db.commit()
        return render_template("descadastrado.html")

    @app.get("/saude")
    def saude():
        return {"status": "ok"}

    @app.get("/admin/login")
    def admin_login():
        if session.get("admin"):
            return redirect(url_for("admin_painel"))
        return render_template("admin/login.html")

    @app.post("/admin/login")
    def admin_login_post():
        senha = request.form.get("senha", "")
        if hmac.compare_digest(senha, current_app.config["ADMIN_PASSWORD"]):
            session.clear()
            session["admin"] = True
            session["_csrf"] = secrets.token_hex(16)
            destino = request.args.get("next") or url_for("admin_painel")
            if not destino.startswith("/"):
                destino = url_for("admin_painel")
            return redirect(destino)
        flash("Senha incorreta.", "erro")
        return render_template("admin/login.html"), 401

    @app.post("/admin/logout")
    def admin_logout():
        session.clear()
        return redirect(url_for("index"))

    @app.get("/admin")
    @login_required
    def admin_painel():
        db = get_db()
        lista = db.execute(
            "SELECT * FROM edicoes ORDER BY CAST(numero AS INTEGER) DESC"
        ).fetchall()
        stats = {
            "edicoes": db.execute("SELECT COUNT(*) c FROM edicoes").fetchone()["c"],
            "rascunhos": db.execute(
                "SELECT COUNT(*) c FROM edicoes WHERE status = 'rascunho'"
            ).fetchone()["c"],
            "inscritos": db.execute(
                "SELECT COUNT(*) c FROM inscritos WHERE ativo = 1"
            ).fetchone()["c"],
        }
        return render_template("admin/painel.html", edicoes=lista, stats=stats)

    @app.get("/admin/edicao/nova")
    @login_required
    def admin_edicao_nova():
        return render_template("admin/editor.html", edicao=None, numero_sugerido=proximo_numero())

    @app.post("/admin/edicao/nova")
    @login_required
    def admin_edicao_nova_post():
        if not check_csrf():
            abort(400)
        dados = extrair_dados_edicao()
        if not dados["numero"] or not dados["titulo"]:
            flash("Número e título são obrigatórios.", "erro")
            return render_template(
                "admin/editor.html", edicao=dados, numero_sugerido=dados["numero"] or proximo_numero()
            ), 400
        db = get_db()
        if db.execute(
            "SELECT id FROM edicoes WHERE numero = ?", (dados["numero"],)
        ).fetchone():
            flash("Já existe uma edição com esse número.", "erro")
            return render_template(
                "admin/editor.html", edicao=dados, numero_sugerido=dados["numero"]
            ), 400
        db.execute(
            "INSERT INTO edicoes (numero, titulo, assunto, conteudo_html, documento_completo, status, criada_em)"
            " VALUES (?, ?, ?, ?, 0, 'rascunho', ?)",
            (dados["numero"], dados["titulo"], dados["assunto"], dados["conteudo_html"], agora()),
        )
        db.commit()
        flash("Rascunho criado. Agora é só editar e publicar.", "ok")
        return redirect(url_for("admin_painel"))

    @app.get("/admin/edicao/<int:edicao_id>/editar")
    @login_required
    def admin_edicao_editar(edicao_id):
        edicao = buscar_edicao(edicao_id)
        if not edicao:
            abort(404)
        return render_template("admin/editor.html", edicao=edicao, numero_sugerido=edicao["numero"])

    @app.post("/admin/edicao/<int:edicao_id>/editar")
    @login_required
    def admin_edicao_editar_post(edicao_id):
        if not check_csrf():
            abort(400)
        edicao = buscar_edicao(edicao_id)
        if not edicao:
            abort(404)
        dados = extrair_dados_edicao()
        if not dados["titulo"]:
            flash("O título é obrigatório.", "erro")
            return render_template(
                "admin/editor.html", edicao=dados, numero_sugerido=edicao["numero"]
            ), 400
        get_db().execute(
            "UPDATE edicoes SET titulo = ?, assunto = ?, conteudo_html = ? WHERE id = ?",
            (dados["titulo"], dados["assunto"], dados["conteudo_html"], edicao_id),
        )
        get_db().commit()
        flash("Edição salva.", "ok")
        return redirect(url_for("admin_painel"))

    @app.post("/admin/edicao/<int:edicao_id>/publicar")
    @login_required
    def admin_edicao_publicar(edicao_id):
        if not check_csrf():
            abort(400)
        edicao = buscar_edicao(edicao_id)
        if not edicao:
            abort(404)
        get_db().execute(
            "UPDATE edicoes SET status = 'publicada', publicada_em = COALESCE(publicada_em, ?) WHERE id = ?",
            (agora(), edicao_id),
        )
        get_db().commit()
        flash(f"Edição #{edicao['numero']} publicada no site.", "ok")
        return redirect(url_for("admin_painel"))

    @app.post("/admin/edicao/<int:edicao_id>/excluir")
    @login_required
    def admin_edicao_excluir(edicao_id):
        if not check_csrf():
            abort(400)
        edicao = buscar_edicao(edicao_id)
        if not edicao:
            abort(404)
        db = get_db()
        db.execute("DELETE FROM envios WHERE edicao_id = ?", (edicao_id,))
        db.execute("DELETE FROM edicoes WHERE id = ?", (edicao_id,))
        db.commit()
        flash(f"Edição #{edicao['numero']} excluída.", "info")
        return redirect(url_for("admin_painel"))

    @app.get("/admin/edicao/<int:edicao_id>/visualizar")
    @login_required
    def admin_edicao_visualizar(edicao_id):
        edicao = buscar_edicao(edicao_id)
        if not edicao:
            abort(404)
        return render_template("edicao.html", edicao=edicao, modo_admin=True)

    @app.post("/admin/edicao/<int:edicao_id>/enviar")
    @login_required
    def admin_edicao_enviar(edicao_id):
        if not check_csrf():
            abort(400)
        edicao = buscar_edicao(edicao_id)
        if not edicao:
            abort(404)
        modo = request.form.get("modo", "todos")
        base_url = request.url_root.rstrip("/")
        mailer = mailer_atual()
        db = get_db()
        if modo == "teste":
            email_teste = request.form.get("email_teste", "").strip().lower()
            if not EMAIL_RE.match(email_teste):
                flash("Informe um e-mail válido para o envio de teste.", "erro")
                return redirect(url_for("admin_painel"))
            destinos = [(email_teste, None)]
        else:
            linhas = db.execute(
                "SELECT email, token FROM inscritos WHERE ativo = 1 ORDER BY email"
            ).fetchall()
            destinos = [(r["email"], r["token"]) for r in linhas]
            if not destinos:
                flash("Não há inscritos ativos para enviar.", "erro")
                return redirect(url_for("admin_painel"))
        assunto = edicao["assunto"] or f"Decifrando Dados — Edição #{edicao['numero']}: {edicao['titulo']}"
        enviados = erros = 0
        for email, token in destinos:
            html = montar_email_html(edicao, token, base_url)
            ok, detalhe = mailer.send(email, assunto, html)
            db.execute(
                "INSERT INTO envios (edicao_id, email, status, detalhe, enviado_em) VALUES (?, ?, ?, ?, ?)",
                (edicao_id, email, "enviado" if ok else "erro", detalhe, agora()),
            )
            if ok:
                enviados += 1
            else:
                erros += 1
        if modo == "todos":
            db.execute("UPDATE edicoes SET enviada_em = ? WHERE id = ?", (agora(), edicao_id))
        db.commit()
        if modo == "teste":
            flash(f"E-mail de teste enviado para {email_teste}.", "ok" if not erros else "erro")
        else:
            flash(
                f"Edição #{edicao['numero']} enviada para {enviados} inscrito(s)"
                + (f" ({erros} erro(s))" if erros else "")
                + ".",
                "ok" if not erros else "erro",
            )
        return redirect(url_for("admin_painel"))

    @app.get("/admin/inscritos")
    @login_required
    def admin_inscritos():
        lista = get_db().execute(
            "SELECT * FROM inscritos ORDER BY ativo DESC, criado_em DESC"
        ).fetchall()
        return render_template("admin/inscritos.html", inscritos=lista)

    @app.post("/admin/inscrito/<int:inscrito_id>/remover")
    @login_required
    def admin_inscrito_remover(inscrito_id):
        if not check_csrf():
            abort(400)
        get_db().execute("DELETE FROM inscritos WHERE id = ?", (inscrito_id,))
        get_db().commit()
        flash("Inscrito removido.", "info")
        return redirect(url_for("admin_inscritos"))

    @app.get("/admin/envios/<int:edicao_id>")
    @login_required
    def admin_envios(edicao_id):
        edicao = buscar_edicao(edicao_id)
        if not edicao:
            abort(404)
        lista = get_db().execute(
            "SELECT * FROM envios WHERE edicao_id = ? ORDER BY enviado_em DESC", (edicao_id,)
        ).fetchall()
        return render_template("admin/envios.html", edicao=edicao, envios=lista)


def proximo_numero():
    linha = get_db().execute(
        "SELECT numero FROM edicoes ORDER BY CAST(numero AS INTEGER) DESC LIMIT 1"
    ).fetchone()
    if not linha:
        return "01"
    try:
        return str(int(linha["numero"]) + 1).zfill(2)
    except ValueError:
        return "01"


def extrair_dados_edicao():
    return {
        "numero": request.form.get("numero", "").strip(),
        "titulo": request.form.get("titulo", "").strip(),
        "assunto": request.form.get("assunto", "").strip(),
        "conteudo_html": request.form.get("conteudo_html", ""),
    }


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)
