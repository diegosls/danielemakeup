from flask import Flask, send_from_directory
from flask_cors import CORS
from database import init_db
from routes import register_routes
import os

app = Flask(__name__)
app.secret_key = "chave-secreta-troque-isso"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024 
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

CORS(app, supports_credentials=True, origins=["https://danimakeup.netlify.app"])

if os.path.exists("/app/img"):
    IMG_FOLDER = "/app/img"
else:
    IMG_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img"))

@app.route("/img/<path:filename>")
def servir_imagem(filename):
    return send_from_directory(IMG_FOLDER, filename)

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
