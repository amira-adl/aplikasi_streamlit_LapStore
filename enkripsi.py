import streamlit as st
import pandas as pd
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

# Fungsi padding
def pad(data):
    pad_len = AES.block_size - len(data) % AES.block_size
    return data + chr(pad_len) * pad_len

# Fungsi validasi kunci AES
def get_aes_key_from_input(raw_key: str) -> bytes:
    key_bytes = raw_key.encode("utf-8")
    if len(key_bytes) != 32:
        raise ValueError("Kunci harus 32 karakter (1 karakter = 1 byte untuk AES-256).")
    return key_bytes

# Enkripsi satu field dengan kunci
def encrypt_field_with_key(text, aes_key):
    iv = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    padded = pad(str(text)).encode("utf-8")
    ciphertext = cipher.encrypt(padded)
    return (iv + ciphertext).hex()

# Halaman utama Streamlit
def run_enkripsi_page():
    st.title("🔐 Enkripsi Data LapStore dengan Kunci AES-256")
    st.markdown("Enkripsi data produk dan transaksi menggunakan algoritma AES-256 untuk menjaga keamanan informasi.")

    raw_key = st.text_input("Masukkan kunci AES-256 (32 karakter)", type="password")

    if raw_key and st.button("🔒 Enkripsi Data"):
        try:
            aes_key = get_aes_key_from_input(raw_key)

            # Cek file
            if not os.path.exists("produk_IT.xlsx") or not os.path.exists("transaksi_IT.xlsx"):
                st.error("❌ File Excel tidak ditemukan. Harap pastikan file ada di direktori kerja.")
                return

            # Baca file Excel
            df_produk = pd.read_excel("produk_IT.xlsx")
            df_transaksi = pd.read_excel("transaksi_IT.xlsx")

            # Gabung data (jika jumlah baris sama)
            df = pd.concat([df_transaksi.reset_index(drop=True), df_produk.reset_index(drop=True)], axis=1)

            # Enkripsi per kolom
            encrypted_rows = []
            for _, row in df.iterrows():
                encrypted_row = {col: encrypt_field_with_key(row[col], aes_key) for col in df.columns}
                encrypted_rows.append(encrypted_row)

            df_encrypted = pd.DataFrame(encrypted_rows)

            # Tampilkan dan unduh
            st.success("✅ Data berhasil dienkripsi dengan kunci AES-256!")
            st.dataframe(df_encrypted)

            csv = df_encrypted.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Unduh Data Terenkripsi", csv, "data_terenkripsi.csv", "text/csv")

        except ValueError as e:
            st.error(f"❌ {e}")
