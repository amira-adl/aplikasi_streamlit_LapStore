import sqlite3
import pandas as pd
import streamlit as st

# 🔌 Koneksi
def get_connection():
    return sqlite3.connect("marketplace.db")

# 🧱 Tabel user login
def create_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# 🧱 Inisialisasi tabel utama
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabel produk (dengan kategori)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL,
            kategori TEXT
        )
    """)

    # Tabel transaksi dengan produk_id sebagai foreign key
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produk_id INTEGER,
            jumlah INTEGER,
            total_harga INTEGER,
            waktu TEXT,
            FOREIGN KEY (produk_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    conn.close()

# 🔁 Alias buat dipanggil di app.py
def create_tables():
    create_user_table()
    init_db()

# 🧹 Clear semua data
def clear_all_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM transaksi")
    conn.commit()
    conn.close()


# 🧱 Tambah kolom kategori (opsional jika upgrade dari struktur lama)
def alter_table_add_kategori():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN kategori TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Kolom sudah ada
    conn.close()

# 💼 CRUD Produk
def get_all_products():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products ORDER BY id DESC", conn)
    conn.close()
    return df

def add_product(nama, harga, stok, kategori):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (nama, harga, stok, kategori) VALUES (?, ?, ?, ?)",
        (nama, harga, stok, kategori)
    )
    conn.commit()
    conn.close()

def update_product(id, nama, harga, stok, kategori):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET nama = ?, harga = ?, stok = ?, kategori = ?
        WHERE id = ?
    """, (nama, harga, stok, kategori, id))
    conn.commit()
    conn.close()

def delete_product(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# 📥 Get semua transaksi (tambahan untuk enkripsi)
def get_all_transaksi():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM transaksi ORDER BY id DESC", conn)
    conn.close()
    return df

# 🧾 Opsional: Get semua user (jika ingin enkripsi juga user login)
def get_all_users():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

# 💾 Tambahan: Simpan hasil dekripsi ke tabel produk
def insert_multiple_products(data_produk):
    conn = get_connection()
    cursor = conn.cursor()
    for produk in data_produk:
        cursor.execute("""
            INSERT INTO products (nama, harga, stok, kategori)
            VALUES (?, ?, ?, ?)
        """, (
            produk.get("nama", ""),
            produk.get("harga", 0),
            produk.get("stok", 0),
            produk.get("kategori", "")
        ))
    conn.commit()
    conn.close()

# 💾 Tambahan: Simpan hasil dekripsi ke tabel transaksi
def insert_multiple_transaksi(data_transaksi):
    conn = get_connection()
    cursor = conn.cursor()
    for trx in data_transaksi:
        cursor.execute("""
            INSERT INTO transaksi (produk_id, jumlah, total_harga, waktu)
            VALUES (?, ?, ?, ?)
        """, (
            trx.get("produk_id"),
            trx.get("jumlah", 0),
            trx.get("total_harga", 0),
            trx.get("waktu", "")
        ))
    conn.commit()
    conn.close()

# 💾 Tambahan: Ekspor hasil dekripsi ke file SQLite eksternal
def export_decrypted_to_sqlite(data_produk, data_transaksi, path="decrypted_data.db"):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Tabel produk
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER,
            nama TEXT,
            harga INTEGER,
            stok INTEGER,
            kategori TEXT
        )
    """)
    for p in data_produk:
        cursor.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?)", (
            p.get("id"),
            p.get("nama", ""),
            p.get("harga", 0),
            p.get("stok", 0),
            p.get("kategori", "")
        ))

    # Tabel transaksi
    cursor.execute("DROP TABLE IF EXISTS transaksi")
    cursor.execute("""
        CREATE TABLE transaksi (
            id INTEGER,
            produk_id INTEGER,
            jumlah INTEGER,
            total_harga INTEGER,
            waktu TEXT
        )
    """)
    for t in data_transaksi:
        cursor.execute("INSERT INTO transaksi VALUES (?, ?, ?, ?, ?)", (
            t.get("id"),
            t.get("produk_id"),
            t.get("jumlah", 0),
            t.get("total_harga", 0),
            t.get("waktu", "")
        ))

    conn.commit()
    conn.close()
