import streamlit as st
from database import get_all_products, add_product, update_product, delete_product
from streamlit import cache_data

def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")

def show_kelola_produk():
    st.title("🛠️ Manajemen Produk LapStore")

    # Tombol untuk refresh cache data
    if st.button("🔄 Refresh Data"):
        cache_data.clear()
        st.rerun()

    # Ambil data setelah kemungkinan refresh
    df_produk = get_all_products()

    tab1, tab2, tab3 = st.tabs(["📋 Daftar Produk", "➕ Tambah Produk", "✏️ Edit / Hapus Produk"])

    # 📋 Tab 1: Daftar Produk
    with tab1:
        st.subheader("Daftar Produk")
        if df_produk.empty:
            st.info("Belum ada produk.")
        else:
            df_tampil = df_produk.copy()
            df_tampil["harga"] = df_tampil["harga"].apply(format_rupiah)
            st.dataframe(df_tampil, use_container_width=True)

    # ➕ Tab 2: Tambah Produk
    with tab2:
        st.subheader("Tambah Produk Baru")
        with st.form("form_tambah"):
            kategori = st.text_input("Kategori Produk")
            nama = st.text_input("Nama Produk")
            harga = st.number_input("Harga (Rp)", min_value=0)
            stok = st.number_input("Stok", min_value=0)
            submit = st.form_submit_button("Tambah")
            if submit:
                if nama.strip() == "":
                    st.warning("Nama produk tidak boleh kosong.")
                else:
                    add_product(nama, int(harga), int(stok), kategori)
                    cache_data.clear()
                    st.success("Produk berhasil ditambahkan.")
                    st.rerun()

    # ✏️ Tab 3: Edit / Hapus Produk
    with tab3:
        st.subheader("Edit / Hapus Produk")
        if df_produk.empty:
            st.info("Belum ada produk.")
        else:
            produk_opsi = df_produk.apply(lambda row: f"[{row['id']}] {row['nama']}", axis=1).tolist()
            pilihan = st.selectbox("Pilih Produk", produk_opsi)

            id_pilih = int(pilihan.split("]")[0][1:])
            data_pilih = df_produk[df_produk["id"] == id_pilih].iloc[0]

            nama_baru = st.text_input("Nama Produk", value=data_pilih["nama"])
            harga_baru = st.number_input("Harga (Rp)", min_value=0, value=int(data_pilih["harga"]))
            stok_baru = st.number_input("Stok", min_value=0, value=int(data_pilih["stok"]))
            kategori_baru = st.text_input("Kategori", value=str(data_pilih["kategori"]) if data_pilih["kategori"] else "")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update"):
                    update_product(id_pilih, nama_baru, int(harga_baru), int(stok_baru), kategori_baru)
                    cache_data.clear()
                    st.success("Produk berhasil diperbarui.")
                    st.rerun()

            with col2:
                if st.button("Hapus"):
                    delete_product(id_pilih)
                    cache_data.clear()
                    st.warning("Produk telah dihapus.")
                    st.rerun()
