from flask import jsonify, request, session
import json
import os
from werkzeug.utils import secure_filename
from database import get_db

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}


def extensao_permitida(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS
    )


def row_para_dict(row):
    dados = dict(row)
    dados["destaque"] = bool(dados["destaque"])
    dados["beneficios"] = json.loads(dados["beneficios"] or "[]")
    return dados


def admin_logado():
    return session.get("admin") is True


def register_routes(app):

    # ==========================
    # SERVIÇOS PÚBLICOS
    # ==========================

    @app.route("/api/services", methods=["GET"])
    def listar_servicos():
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM services ORDER BY id DESC"
        ).fetchall()
        conn.close()

        return jsonify({
            "services": [row_para_dict(r) for r in rows]
        })

    # ==========================
    # LOGIN
    # ==========================

    @app.route("/api/admin/login", methods=["POST"])
    def login():

        dados = request.get_json()

        username = dados.get("username", "").strip()
        password = dados.get("password", "").strip()

        conn = get_db()

        admin = conn.execute(
            """
            SELECT *
            FROM admin
            WHERE username = ?
            AND password = ?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if admin:
            session["admin"] = True
            return jsonify({"ok": True})

        return jsonify({
            "ok": False,
            "erro": "Usuário ou senha inválidos."
        }), 401


    @app.route("/api/admin/logout", methods=["POST"])
    def logout():
        session.clear()
        return jsonify({"ok": True})


    @app.route("/api/admin/check", methods=["GET"])
    def check_auth():
        return jsonify({
            "logado": admin_logado()
        })

    # ==========================
    # UPLOAD
    # ==========================

    @app.route("/api/admin/upload", methods=["POST"])
    def upload_imagem():

        if not admin_logado():
            return jsonify({"erro": "Não autorizado"}), 401

        if "imagem" not in request.files:
            return jsonify({"erro": "Nenhuma imagem enviada"}), 400

        arquivo = request.files["imagem"]

        if arquivo.filename == "":
            return jsonify({"erro": "Arquivo inválido"}), 400

        if not extensao_permitida(arquivo.filename):
            return jsonify({"erro": "Formato não permitido"}), 400

        filename = secure_filename(arquivo.filename)

        if os.path.exists("/app/img"):
            pasta = "/app/img"
        else:
            pasta = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "img")
            )

        os.makedirs(pasta, exist_ok=True)

        arquivo.save(os.path.join(pasta, filename))

        return jsonify({
            "ok": True,
            "imagem": f"img/{filename}"
        })

    # ==========================
    # CRIAR SERVIÇO
    # ==========================

    @app.route("/api/admin/services", methods=["POST"])
    def criar_servico():

        if not admin_logado():
            return jsonify({"erro": "Não autorizado"}), 401

        d = request.get_json()

        conn = get_db()

        cursor = conn.execute("""
            INSERT INTO services (
                titulo,
                descricao,
                imagem,
                mensagem,
                tempo,
                categoria,
                destaque,
                beneficios
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d.get("titulo", ""),
            d.get("descricao", ""),
            d.get("imagem", ""),
            d.get("mensagem", ""),
            d.get("tempo", ""),
            d.get("categoria", ""),
            1 if d.get("destaque") else 0,
            json.dumps(d.get("beneficios", []), ensure_ascii=False)
        ))

        conn.commit()

        novo_id = cursor.lastrowid

        conn.close()

        return jsonify({
            "ok": True,
            "id": novo_id
        }), 201

    # ==========================
    # EDITAR
    # ==========================

    @app.route("/api/admin/services/<int:id>", methods=["PUT"])
    def editar_servico(id):

        if not admin_logado():
            return jsonify({"erro": "Não autorizado"}), 401

        d = request.get_json()

        conn = get_db()

        cursor = conn.execute("""
            UPDATE services
            SET
                titulo=?,
                descricao=?,
                imagem=?,
                mensagem=?,
                tempo=?,
                categoria=?,
                destaque=?,
                beneficios=?
            WHERE id=?
        """, (
            d.get("titulo", ""),
            d.get("descricao", ""),
            d.get("imagem", ""),
            d.get("mensagem", ""),
            d.get("tempo", ""),
            d.get("categoria", ""),
            1 if d.get("destaque") else 0,
            json.dumps(d.get("beneficios", []), ensure_ascii=False),
            id
        ))

        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                "erro": "Serviço não encontrado."
            }), 404

        conn.close()

        return jsonify({
            "ok": True
        })

    # ==========================
    # EXCLUIR
    # ==========================

    @app.route("/api/admin/services/<int:id>", methods=["DELETE"])
    def deletar_servico(id):

        if not admin_logado():
            return jsonify({"erro": "Não autorizado"}), 401

        conn = get_db()

        cursor = conn.execute(
            "DELETE FROM services WHERE id=?",
            (id,)
        )

        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                "erro": "Serviço não encontrado."
            }), 404

        conn.close()

        return jsonify({
            "ok": True
        })
