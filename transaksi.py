import streamlit as st
import pandas as pd
from database import get_connection
from datetime import datetime

def get_all_transaksi():
    conn = get_connection()
    query = """
        SELECT t.id, p.nama AS produk, t.jumlah, t.total_harga, t.waktu
        FROM transaksi t
        JOIN products p ON t.produk_id = p.id
        ORDER BY t.waktu DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def format_rupiah(nominal):
    return f"Rp. {nominal:,.0f}".replace(",", ".")

def format_waktu(waktu):
    try:
        dt = datetime.strptime(waktu, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %B %Y %H:%M")
    except:
        return waktu

def show_transaksi():
    st.title("🧾 Riwayat Transaksi LapStore")

    df = get_all_transaksi()

    if df.empty:
        st.info("Belum ada transaksi yang tercatat.")
        return

    # Format kolom harga dan waktu
    df["total_harga"] = df["total_harga"].apply(lambda x: format_rupiah(int(x)))
    df["waktu"] = df["waktu"].apply(format_waktu)

    # Tampilkan tabel
    st.dataframe(df.rename(columns={
        "id": "ID",
        "produk": "Produk",
        "jumlah": "Jumlah",
        "total_harga": "Total Harga",
        "waktu": "Waktu Transaksi"
    }), use_container_width=True)

    st.caption("📌 Riwayat transaksi ditampilkan secara otomatis berdasarkan waktu terbaru.")
