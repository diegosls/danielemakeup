from flask import jsonify, request, session, current_app
import json
import os
from werkzeug.utils import secure_filename
from database import get_db

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}

def extensao_permitida(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS

def row_para_dict(row):
    d = dict(row)
    d["destaque"] = bool(d["destaque"])
    d["beneficios"] = json.loads(d["beneficios"] or "[]")
    return d

def admin_logado():
    return session.get("admin") is True


def register_routes(app):

    # ── Pública ──
    @app.route("/api/services", methods=["GET"])
    def listar_servicos():
        conn = get_db()
        rows = conn.execute("SELECT * FROM services").fetchall()
        conn.close()
        return jsonify({"services": [row_para_dict(r) for r in rows]})

    # ── Auth ──
    @app.route("/api/admin/login", methods=["POST"])
    def login():
        dados = request.get_json()
        username = dados.get("username", "").strip()
        password = dados.get("password", "").strip()

        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if admin:
            session["admin"] = True
            return jsonify({"ok": True})
        return jsonify({"ok": False, "erro": "Usuário ou senha inválidos"}), 401

    @app.route("/api/admin/logout", methods=["POST"])
    def logout():
        session.clear()
        return jsonify({"ok": True})

    @app.route("/api/admin/check", methods=["GET"])
    def check_auth():
        return jsonify({"logado": admin_logado()})

    # ── Upload de imagem ──
    @app.route("/api/admin/upload", methods=["POST"])
    def upload_imagem():
        if not admin_logado():
            return jsonify({"erro": "Não autorizado"}), 401

        if "imagem" not in request.files:
            return jsonify({"erro": "Nenhuma imagem enviada"}), 400

        arquivo = request.files["imagem"]

        if arquivo.filename == "":
            return jsonify({"erro": "Nome de arquivo vazio"}), 400

        if not extensao_permitida(arquivo.filename):
            return jsonify({"erro": "Formato não permitido. Use PNG, JPG, JPEG, WEBP ou GIF"}), 400

        filename = secure_filename(arquivo.filename)
        pasta_img = os.path.join(current_app.root_path, "..", "img")
        pasta_img = os.path.abspath(pasta_img)
        os.makedirs(pasta_img, exist_ok=True)

        caminho = os.path.join(pasta_img, filename)
        arquivo.save(caminho)

        return jsonify({"ok": True, "imagem": f"img/{filename}"})

    # ── CRUD protegido ──
    @app.route("/api/admin/services", methods=["POST"])
    def criar_servico():
        if not admin_logado():
            return jsonify({"erro": "Não autorizado"}), 401

        d = request.get_json()
        conn = get_db()
        conn.execute("""
            INSERT INTO services (titulo, descricao, imagem, mensagem, tempo, categoria, destaque, beneficios)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d.get("titulo", ""), d.get("descricao", ""), d.get("imagem", ""),
            d.get("mensagem", ""), d.get("tempo", ""), d.get("categoria", ""),
            1 if d.get("destaque") else 0,
            json.dumps(d.get("beneficios", []), ensure_ascii=False)
        ))
        conn.commit()
        conn.close()
        return jsonify({"ok": True}), 201

    @app.route("/api/admin/services/<int:id>", methods=["PUT"])
    def editar_servico(id):
        if not admin_logado():
            return jsonify({"erro": "Não autorizado"}), 401

        d = request.get_json()
        conn = get_db()
        conn.execute("""
            UPDATE services
            SET titulo=?, descricao=?, imagem=?, mensagem=?, tempo=?, categoria=?, destaque=?, beneficios=?
            WHERE id=?
        """, (
            d.get("titulo", ""), d.get("descricao", ""), d.get("imagem", ""),
            d.get("mensagem", ""), d.get("tempo", ""), d.get("categoria", ""),
            1 if d.get("destaque") else 0,
            json.dumps(d.get("beneficios", []), ensure_ascii=False),
            id
        ))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})

    @app.route("/api/admin/services/<int:id>", methods=["DELETE"])
    def deletar_servico(id):
        if not admin_logado():
            return jsonify({"erro": "Não autorizado"}), 401

        conn = get_db()
        conn.execute("DELETE FROM services WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})