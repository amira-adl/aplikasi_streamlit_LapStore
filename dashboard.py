import pandas as pd
from database import get_connection, clear_all_data
from datetime import datetime

# ✅ Tambahan fungsi get_dashboard_data
def get_dashboard_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Jumlah produk
    cursor.execute("SELECT COUNT(*) FROM products")
    jumlah_produk = cursor.fetchone()[0] or 0

    # Total transaksi
    cursor.execute("SELECT COUNT(*) FROM transaksi")
    total_transaksi = cursor.fetchone()[0] or 0

    # Total pendapatan
    cursor.execute("SELECT SUM(total_harga) FROM transaksi")
    result = cursor.fetchone()[0]
    total_pendapatan = result if result is not None else 0

    # Produk terlaris
    cursor.execute("""
        SELECT p.nama, COUNT(*) as jumlah
        FROM transaksi t
        JOIN products p ON t.produk_id = p.id
        GROUP BY p.nama
        ORDER BY jumlah DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    produk_terlaris = result[0] if result else "-"

    # Transaksi terakhir
    cursor.execute("SELECT waktu FROM transaksi ORDER BY waktu DESC LIMIT 1")
    result = cursor.fetchone()
    transaksi_terakhir = result[0] if result else "-"

    conn.close()
    return jumlah_produk, total_transaksi, total_pendapatan, produk_terlaris, transaksi_terakhir


# =======================

def upload_excel_to_database(products_file, transaksi_file, clear=False):
    conn = get_connection()
    cursor = conn.cursor()

    if clear:
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM transaksi")

    # =======================
    # 🔁 PROSES DATA PRODUK
    # =======================
    if products_file:
        df_produk = pd.read_excel(products_file)
        print("📥 Jumlah produk di file Excel:", len(df_produk))

        for _, row in df_produk.iterrows():
            # Validasi data penting
            if pd.isna(row["nama"]) or pd.isna(row["harga"]) or pd.isna(row["stok"]):
                print(f"⚠️ Data produk tidak lengkap, dilewati: {row.to_dict()}")
                continue

            kategori = row["kategori"] if "kategori" in row and not pd.isna(row["kategori"]) else ""
            try:
                cursor.execute("""
                    INSERT INTO products (nama, harga, stok, kategori)
                    VALUES (?, ?, ?, ?)
                """, (row["nama"], row["harga"], row["stok"], kategori))
                print(f"✅ Produk dimasukkan: {row['nama']}")
            except Exception as e:
                print(f"❌ Gagal insert produk '{row['nama']}': {e}")

        cursor.execute("SELECT COUNT(*) FROM products")
        print("📦 Total produk di database sekarang:", cursor.fetchone()[0])

    # =======================
    # 🔁 PROSES DATA TRANSAKSI
    # =======================
    if transaksi_file:
        df_trans = pd.read_excel(transaksi_file)
        print("📥 Jumlah transaksi di file Excel:", len(df_trans))

        for _, row in df_trans.iterrows():
            waktu = row["waktu"]

            # Tangani waktu dalam berbagai format
            try:
                if pd.isna(waktu):
                    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(waktu, pd.Timestamp):
                    waktu = waktu.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(waktu, str):
                    waktu = pd.to_datetime(waktu).strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(waktu, (int, float)):
                    waktu = pd.to_datetime("1899-12-30") + pd.to_timedelta(waktu, unit="D")
                    waktu = waktu.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    waktu = str(waktu)
            except Exception as e:
                print(f"⚠️ Format waktu tidak dikenali: {row['waktu']} | Error: {e}")
                waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # ✅ Insert transaksi
            nama_produk = row["produk"].strip().lower()
            cursor.execute("SELECT id FROM products WHERE LOWER(nama) = ?", (nama_produk,))
            result = cursor.fetchone()

            if result:
                produk_id = result[0]
                cursor.execute("""
                    INSERT INTO transaksi (produk_id, jumlah, total_harga, waktu)
                    VALUES (?, ?, ?, ?)
                """, (produk_id, row["jumlah"], row["total_harga"], waktu))
                print(f"✅ Transaksi ditambahkan: {row['produk']} - {row['jumlah']} item")
            else:
                print(f"⚠️ Produk tidak ditemukan: {row['produk']}")

    conn.commit()
    conn.close()

# =======================

def show_dashboard(st):
    st.title("📈 LapStore – Statistik & Penjualan")



    st.subheader("📥 Unggah Data")
    products_file = st.file_uploader("Unggah Data Produk (products.xlsx)", type=["xlsx"])
    transaksi_file = st.file_uploader("Unggah Data Transaksi (transaksi.xlsx)", type=["xlsx"])
    clear = st.checkbox("🔄 Hapus data lama sebelum simpan")

    if st.button("Proses & Simpan ke Database"):
        if not products_file and not transaksi_file:
            st.warning("Mohon unggah minimal satu file Excel.")
        else:
            upload_excel_to_database(products_file, transaksi_file, clear)
            st.success("Data berhasil diproses dan disimpan!")
            st.rerun()

    st.divider()
    st.subheader("📈 Statistik Penjualan & Produk")

    jumlah_produk, total_transaksi, total_pendapatan, produk_terlaris, transaksi_terakhir = get_dashboard_data()

    col1, col2 = st.columns(2)
    col1.metric("📦 Jumlah Produk", jumlah_produk)
    col2.metric("💳 Total Transaksi", total_transaksi)

    col1, col2 = st.columns(2)
    col1.metric("💰 Total Pendapatan", f"Rp {total_pendapatan:,.0f}".replace(",", "."))
    col2.metric("🔥 Produk Terlaris", produk_terlaris)

    st.metric("🕓 Transaksi Terakhir", transaksi_terakhir)

    st.divider()
    st.subheader("🧹 Manajemen Data")

    if st.button("🧹 Hapus Semua Data"):
        clear_all_data()
        st.success("Semua data berhasil dihapus dari database.")
        st.rerun()