import streamlit as st
from auth import login_user, register_user
from database import create_user_table, create_tables, alter_table_add_kategori
from dashboard import show_dashboard
from kelola import show_kelola_produk
from transaksi import show_transaksi
from enkripsi import run_enkripsi_page
from dekripsi import run_dekripsi_csv_page

# Inisialisasi database
create_user_table()
create_tables()
alter_table_add_kategori()

st.set_page_config(page_title="LapStore Login", page_icon="💻", layout="centered")

if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"]:
    st.sidebar.success(f"👤 {st.session_state['user']}")
    menu = st.sidebar.selectbox(
        "Menu",
        [
            "📊 Statistik Penjualan",
            "🛒 Kelola Produk",
            "🧾 Riwayat Transaksi",
            "🔐 Enkripsi Data",
            "🔓 Dekripsi Data",
            "🚪 Logout"
        ]
    )

    if menu == "📊 Statistik Penjualan":
        show_dashboard(st)
    elif menu == "🛒 Kelola Produk":
        show_kelola_produk()
    elif menu == "🧾 Riwayat Transaksi":
        show_transaksi()
    elif menu == "🔐 Enkripsi Data":
        run_enkripsi_page()
    elif menu == "🔓 Dekripsi Data":
        run_dekripsi_csv_page()
    elif menu == "🚪 Logout":
        st.session_state["user"] = None
        st.rerun()

else:
    st.title("💻 LapStore – Platform Produk Teknologi")
    menu = st.sidebar.selectbox("Menu", ["Login", "Daftar"])

    if menu == "Login":
        st.subheader("Masuk ke Platform")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.success(f"Selamat datang, {username}!")
                st.session_state["user"] = username
                st.rerun()
            else:
                st.error("Username atau password salah.")

    elif menu == "Daftar":
        st.subheader("Buat Akun Baru")
        username = st.text_input("Buat Username")
        password = st.text_input("Buat Password", type="password")
        confirm = st.text_input("Ulangi Password", type="password")

        if st.button("Daftar"):
            if password != confirm:
                st.warning("Password tidak cocok!")
            elif register_user(username, password):
                st.success("Registrasi berhasil. Silakan login.")
            else:
                st.error("Username sudah terdaftar.")
