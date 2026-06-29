from flask import Flask, send_from_directory
from flask_cors import CORS
from database import init_db
from routes import register_routes
import os

app = Flask(__name__)

# Configurações
app.secret_key = os.environ.get("SECRET_KEY", "chave-secreta-troque-isso")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True

# CORS
CORS(
    app,
    supports_credentials=True,
    origins=["https://danimakeup.netlify.app"]
)

# Inicializa o banco de dados
init_db()

# Pasta das imagens
if os.path.exists("/app/img"):
    IMG_FOLDER = "/app/img"
else:
    IMG_FOLDER = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "img")
    )

# Servir imagens
@app.route("/img/<path:filename>")
def servir_imagem(filename):
    return send_from_directory(IMG_FOLDER, filename)

# Registra as rotas da API
register_routes(app)

# Executa localmente
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
