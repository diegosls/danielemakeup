import sqlite3
import json
import sys
import os

# Garante que o data.py da mesma pasta seja encontrado
sys.path.insert(0, os.path.dirname(__file__))
from data import services as services_iniciais

# ALTERADO: Em produção (Render), salva no disco persistente. Localmente, usa a pasta atual.
if os.path.exists("/app/img"):
    DB_PATH = "/app/img/database.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo     TEXT    NOT NULL,
            descricao  TEXT,
            imagem     TEXT,
            mensagem   TEXT,
            tempo      TEXT,
            categoria  TEXT,
            destaque   INTEGER DEFAULT 0,
            beneficios TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id       INTEGER PRIMARY KEY,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO admin (id, username, password)
        VALUES (1, 'daniele', 'admin123')
    """)

    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        for s in services_iniciais:
            cursor.execute("""
                INSERT INTO services (titulo, descricao, imagem, mensagem, tempo, categoria, destaque, beneficios)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["titulo"], s["descricao"], s["imagem"], s["mensagem"],
                s["tempo"], s["categoria"], 1 if s["destaque"] else 0,
                json.dumps(s["beneficios"], ensure_ascii=False)
            ))

    conn.commit()
    conn.close()
