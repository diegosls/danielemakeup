import sqlite3
import json
import sys
import os

# Garante que o data.py da mesma pasta seja encontrado
sys.path.insert(0, os.path.dirname(__file__))
from data import services as services_iniciais

# Caminho do banco
if os.path.exists("/app/img"):
    DB_PATH = "/app/img/database.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    # Garante que a pasta do banco exista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    # Tabela de serviços
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            imagem TEXT,
            mensagem TEXT,
            tempo TEXT,
            categoria TEXT,
            destaque INTEGER DEFAULT 0,
            beneficios TEXT
        )
    """)

    # Tabela do administrador
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # Usuário padrão
    cursor.execute("""
        INSERT OR IGNORE INTO admin (id, username, password)
        VALUES (1, ?, ?)
    """, (
        "daniele",
        "admin123"
    ))

    # Popula os serviços apenas uma vez
    cursor.execute("SELECT COUNT(*) FROM services")
    quantidade = cursor.fetchone()[0]

    if quantidade == 0:

        for servico in services_iniciais:

            cursor.execute("""
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

                servico.get("titulo", ""),
                servico.get("descricao", ""),
                servico.get("imagem", ""),
                servico.get("mensagem", ""),
                servico.get("tempo", ""),
                servico.get("categoria", ""),
                1 if servico.get("destaque") else 0,
                json.dumps(
                    servico.get("beneficios", []),
                    ensure_ascii=False
                )

            ))

    conn.commit()
    conn.close()
