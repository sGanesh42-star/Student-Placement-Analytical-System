import sqlite3
from flask import g

DATABASE = "placement.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL, role TEXT DEFAULT 'student')""")
    db.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, cgpa REAL NOT NULL, aptitude REAL NOT NULL,
        communication REAL NOT NULL, internships INTEGER NOT NULL, projects INTEGER NOT NULL,
        result TEXT NOT NULL, probability REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id))""")
    # Demo admin account: admin@placement.com / Admin123!
    from werkzeug.security import generate_password_hash
    exists = db.execute("SELECT id FROM users WHERE email=?", ("admin@placement.com",)).fetchone()
    if not exists:
        db.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                   ("Administrator", "admin@placement.com", generate_password_hash("Admin123!"), "admin"))
    db.commit()
    db.close()
