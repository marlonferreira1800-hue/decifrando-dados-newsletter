import os
import sys
import tempfile
import unittest

_TMP_IMPORT = tempfile.mkdtemp(prefix="newsletter-import-")
os.environ.setdefault("DATABASE", os.path.join(_TMP_IMPORT, "import-time.db"))
os.environ.setdefault("SECRET_KEY", "teste-import")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from db import get_db
from mailer import LogMailer


class NewsletterTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mailer = LogMailer()
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "teste",
                "ADMIN_PASSWORD": "segredo",
                "DATABASE": os.path.join(self.tmp.name, "teste.db"),
                "PUBLICACOES_DIR": os.path.join(self.tmp.name, "sem-publicacoes"),
                "SEED_ON_INIT": False,
                "MAILER": self.mailer,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def login(self):
        resp = self.client.post("/admin/login", data={"senha": "segredo"}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        with self.client.session_transaction() as sess:
            self.csrf = sess["_csrf"]
        return resp

    def criar_edicao(self, numero="01", titulo="Primeira edição", conteudo="<p>Olá</p>"):
        return self.client.post(
            "/admin/edicao/nova",
            data={
                "_csrf": self.csrf,
                "numero": numero,
                "titulo": titulo,
                "assunto": "Assunto teste",
                "conteudo_html": conteudo,
            },
            follow_redirects=False,
        )

    def test_pagina_inicial(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Decifrando Dados", resp.data)

    def test_saude(self):
        resp = self.client.get("/saude")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "ok"})

    def test_inscricao_e_duplicidade(self):
        resp = self.client.post("/inscrever-se", data={"email": "Leitor@Exemplo.com"})
        self.assertEqual(resp.status_code, 302)
        with self.app.app_context():
            linhas = get_db().execute("SELECT email, ativo FROM inscritos").fetchall()
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["email"], "leitor@exemplo.com")
        self.assertEqual(linhas[0]["ativo"], 1)
        self.client.post("/inscrever-se", data={"email": "leitor@exemplo.com"})
        with self.app.app_context():
            total = get_db().execute("SELECT COUNT(*) c FROM inscritos").fetchone()["c"]
        self.assertEqual(total, 1)

    def test_inscricao_email_invalido(self):
        resp = self.client.post("/inscrever-se", data={"email": "nao-e-email"})
        self.assertEqual(resp.status_code, 302)
        with self.app.app_context():
            total = get_db().execute("SELECT COUNT(*) c FROM inscritos").fetchone()["c"]
        self.assertEqual(total, 0)

    def test_admin_exige_login(self):
        resp = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/admin/login", resp.headers["Location"])

    def test_login_senha_errada_e_certa(self):
        resp = self.client.post("/admin/login", data={"senha": "errada"})
        self.assertEqual(resp.status_code, 401)
        self.login()
        resp = self.client.get("/admin")
        self.assertEqual(resp.status_code, 200)

    def test_criar_publicar_e_ver_edicao(self):
        self.login()
        resp = self.criar_edicao()
        self.assertEqual(resp.status_code, 302)
        with self.app.app_context():
            ed = get_db().execute("SELECT * FROM edicoes WHERE numero = '01'").fetchone()
            edicao_id = ed["id"]
            self.assertEqual(ed["status"], "rascunho")
        resp = self.client.get(f"/edicao/{edicao_id}")
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(f"/admin/edicao/{edicao_id}/publicar", data={"_csrf": self.csrf})
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get(f"/edicao/{edicao_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Primeira edi", resp.data)
        resp = self.client.get("/edicoes")
        self.assertIn(b"Primeira edi", resp.data)

    def test_criar_edicao_sem_csrf_rejeitado(self):
        self.login()
        resp = self.client.post(
            "/admin/edicao/nova",
            data={"numero": "01", "titulo": "X", "assunto": "", "conteudo_html": ""},
        )
        self.assertEqual(resp.status_code, 400)

    def test_envio_para_todos_registra_outbox_e_log(self):
        self.login()
        self.client.post("/inscrever-se", data={"email": "a@exemplo.com"})
        self.client.post("/inscrever-se", data={"email": "b@exemplo.com"})
        self.criar_edicao()
        with self.app.app_context():
            edicao_id = get_db().execute("SELECT id FROM edicoes WHERE numero='01'").fetchone()["id"]
        resp = self.client.post(
            f"/admin/edicao/{edicao_id}/enviar", data={"_csrf": self.csrf, "modo": "todos"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(self.mailer.outbox), 2)
        destinos = sorted(m["para"] for m in self.mailer.outbox)
        self.assertEqual(destinos, ["a@exemplo.com", "b@exemplo.com"])
        self.assertIn("Descadastrar", self.mailer.outbox[0]["html"])
        with self.app.app_context():
            envios = get_db().execute("SELECT * FROM envios WHERE edicao_id = ?", (edicao_id,)).fetchall()
            ed = get_db().execute("SELECT enviada_em FROM edicoes WHERE id = ?", (edicao_id,)).fetchone()
        self.assertEqual(len(envios), 2)
        self.assertTrue(all(e["status"] == "enviado" for e in envios))
        self.assertIsNotNone(ed["enviada_em"])

    def test_envio_teste(self):
        self.login()
        self.criar_edicao()
        with self.app.app_context():
            edicao_id = get_db().execute("SELECT id FROM edicoes WHERE numero='01'").fetchone()["id"]
        resp = self.client.post(
            f"/admin/edicao/{edicao_id}/enviar",
            data={"_csrf": self.csrf, "modo": "teste", "email_teste": "teste@exemplo.com"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(self.mailer.outbox), 1)
        self.assertEqual(self.mailer.outbox[0]["para"], "teste@exemplo.com")

    def test_descadastro(self):
        self.client.post("/inscrever-se", data={"email": "sai@exemplo.com"})
        with self.app.app_context():
            token = get_db().execute(
                "SELECT token FROM inscritos WHERE email = 'sai@exemplo.com'"
            ).fetchone()["token"]
        resp = self.client.get(f"/descadastrar/{token}")
        self.assertEqual(resp.status_code, 200)
        with self.client.session_transaction() as sess:
            csrf = sess.get("_csrf")
        if not csrf:
            with self.client.session_transaction() as sess:
                sess["_csrf"] = "tok"
            csrf = "tok"
        resp = self.client.post(f"/descadastrar/{token}", data={"_csrf": csrf})
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            ativo = get_db().execute(
                "SELECT ativo FROM inscritos WHERE email = 'sai@exemplo.com'"
            ).fetchone()["ativo"]
        self.assertEqual(ativo, 0)

    def test_seed_importa_publicacoes(self):
        diretorio = os.path.join(self.tmp.name, "pubs")
        os.makedirs(diretorio, exist_ok=True)
        with open(os.path.join(diretorio, "edicao-07.html"), "w", encoding="utf-8") as arq:
            arq.write(
                "<html><head><title>Título da Edição 07 | Decifrando Dados</title></head>"
                "<body><h1>Olá</h1></body></html>"
            )
        app2 = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "teste",
                "ADMIN_PASSWORD": "x",
                "DATABASE": os.path.join(self.tmp.name, "seed.db"),
                "PUBLICACOES_DIR": diretorio,
                "SEED_ON_INIT": True,
                "MAILER": self.mailer,
            }
        )
        with app2.app_context():
            ed = get_db().execute("SELECT * FROM edicoes WHERE numero = '07'").fetchone()
        self.assertIsNotNone(ed)
        self.assertEqual(ed["titulo"], "Título da Edição 07")
        self.assertEqual(ed["status"], "publicada")
        self.assertEqual(ed["documento_completo"], 1)


if __name__ == "__main__":
    unittest.main()
