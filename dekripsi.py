import streamlit as st
import pandas as pd
from Crypto.Cipher import AES
from io import BytesIO
from fpdf import FPDF

# === Fungsi bantu unpadding
def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

# === Ambil kunci dari input user
def get_aes_key_from_input(raw_key: str) -> bytes:
    if len(raw_key) != 32:
        raise ValueError("Kunci harus tepat 32 karakter (AES-256).")
    return raw_key.encode("utf-8")

# === Fungsi dekripsi tiap field terenkripsi
def decrypt_field(hex_data, aes_key):
    if pd.isna(hex_data) or str(hex_data).strip() == "":
        return "[EMPTY]"
    try:
        raw = bytes.fromhex(str(hex_data).strip())
        if len(raw) < 32:
            return "[INVALID]"  # IV (16) + minimal ciphertext
        iv = raw[:16]
        ciphertext = raw[16:]
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        unpadded = decrypted[:-decrypted[-1]].decode("utf-8", errors="ignore")

        if not unpadded.strip():
            return "[BLANK_RESULT]"

        if unpadded.endswith(".0"):
            try:
                return str(int(float(unpadded)))
            except:
                return unpadded
        return unpadded
    except Exception:
        return "[DECRYPTION_FAILED]"


# === Fungsi buat PDF dari DataFrame
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)
    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode('latin-1'))
    buffer.seek(0)
    return buffer

# === Fungsi utama untuk halaman dekripsi CSV
def run_dekripsi_csv_page():
    st.title("🔓 Dekripsi File Terenkripsi")
    st.info("Unggah file CSV yang berisi data terenkripsi dan masukkan kunci AES-256 (32 karakter).")

    uploaded_file = st.file_uploader("📤 Unggah file CSV terenkripsi", type=["csv"])
    password = st.text_input("🔑 Masukkan kunci AES-256", type="password")

    if uploaded_file and password:
        try:
            aes_key = get_aes_key_from_input(password)
        except ValueError as ve:
            st.error(f"❌ {ve}")
            return

        try:
            df_encrypted = pd.read_csv(uploaded_file, keep_default_na=False)
        except Exception as e:
            st.error(f"❌ Gagal membaca file CSV: {e}")
            return

        # Dekripsi seluruh DataFrame menggunakan applymap
        df_decrypted = df_encrypted.apply(lambda col: col.map(lambda val: decrypt_field(val, aes_key)))
        df_decrypted = df_decrypted.astype(str)

        st.success("✅ Data berhasil didekripsi!")
        st.dataframe(df_decrypted)

        # Unduh CSV
        csv_data = df_decrypted.to_csv(index=False, na_rep="[NULL]").encode()
        st.download_button("📥 Unduh Data CSV", csv_data, "data_didekripsi.csv", "text/csv")

        # Unduh PDF
        pdf_buffer = generate_pdf(df_decrypted)
        st.download_button("📄 Unduh PDF", data=pdf_buffer, file_name="data_didekripsi.pdf", mime="application/pdf")

    else:
        st.warning("Silakan unggah file CSV dan masukkan kunci terlebih dahulu.")
