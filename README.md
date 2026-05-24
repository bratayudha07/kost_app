# 🏠 Aplikasi Manajemen Kost

> Tugas Akhir Mata Kuliah **Basis Data**
> Dosen Pengampu: **Pak Abdun Wijaya**
> Program Studi Informatika — UIN Siber Syekh Nurjati Cirebon

---

## 👥 Kelompok 5

| No | Nama | NIM |
|----|------|-----|
| 1 | Wafah Khonia | 2530801081 |
| 2 | Abil Ghinaya Azka | 2530801056 |
| 3 | Robbi Hamdi | 2530801057 |
| 4 | Hafidzar Ashyawal Sinatryas | 2530801075 |
| 5 | Kalin Aulia Haifa | 2530801068 |

---

## 📖 Tentang Aplikasi

**Aplikasi Manajemen Kost** adalah sistem informasi berbasis web yang dirancang untuk membantu ibu kost dalam mengelola data kamar, penghuni, dan pembayaran sewa secara digital. Aplikasi ini menggantikan pencatatan manual yang rentan terhadap kesalahan dan kehilangan data.

### 🎯 Tujuan

- Mempermudah pengelolaan data penghuni kost
- Memantau status pembayaran sewa setiap bulan secara real-time
- Menyimpan riwayat penghuni dan pembayaran secara terstruktur
- Menyediakan laporan yang dapat diekspor dalam format CSV

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🔐 **Login** | Autentikasi dengan username & password, session persisten |
| 📊 **Dashboard** | Ringkasan total kamar, penghuni aktif, dan status pembayaran bulan berjalan |
| 🏠 **Manajemen Kamar** | Tambah, edit, dan hapus data kamar beserta harga sewa |
| 👥 **Manajemen Penghuni** | Tambah, edit, nonaktifkan, dan hapus data penghuni |
| 💰 **Pembayaran Bulanan** | Tandai status lunas/belum per penghuni per bulan |
| 📋 **Riwayat** | Lihat riwayat pembayaran per penghuni dan riwayat penghuni per kamar |
| 🏚️ **Kamar Kosong** | Pantau kamar yang tidak berpenghuni aktif |
| 📤 **Export Data** | Unduh rekap data dalam format CSV |
| ⚙️ **Pengaturan** | Ubah username dan password akun |

---

## 🗄️ Struktur Database

Aplikasi menggunakan **SQLite** dengan 4 tabel utama:

```
users        → data akun login ibu kost
kamar        → data kamar (nomor, harga sewa)
penghuni     → data penghuni (nama, alamat, no. HP, no. rekening, tanggal masuk/keluar)
pembayaran   → status pembayaran bulanan per penghuni
```

### Relasi Antar Tabel

```
kamar ──< penghuni ──< pembayaran
```

- Satu kamar dapat dihuni oleh lebih dari satu penghuni
- Setiap penghuni memiliki riwayat pembayaran per bulan
- Data penghuni yang keluar tetap tersimpan sebagai riwayat (soft delete)

---

## 🛠️ Teknologi yang Digunakan

| Teknologi | Kegunaan |
|-----------|----------|
| Python 3.12 | Bahasa pemrograman utama |
| Streamlit | Framework web UI |
| SQLite | Database |
| Pandas | Pengolahan dan ekspor data |
| Docker | Containerisasi aplikasi |
| Railway | Platform deployment |

---

## 🚀 Cara Menjalankan Lokal

**1. Clone repository**
```bash
git clone https://github.com/bratayudha07/kost_app.git
cd kost_app
```

**2. Install dependencies**
```bash
# Menggunakan uv (direkomendasikan)
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Atau menggunakan pip biasa
pip install -r requirements.txt
```

**3. Jalankan aplikasi**
```bash
streamlit run app.py
```

**4. Login**
```
Username : admin
Password : kelompok5
```

---

## 🌐 Demo Aplikasi

Aplikasi telah di-deploy dan dapat diakses di:

**🔗 https://ibukostapp.up.railway.app**

---

## 📁 Struktur File

```
kost_app/
├── app.py            # Aplikasi Streamlit (UI & routing)
├── database.py       # Fungsi-fungsi query database
├── schema.sql        # Skema tabel database
├── requirements.txt  # Daftar dependencies
├── Dockerfile        # Konfigurasi Docker
├── railway.toml      # Konfigurasi Railway
└── README.md         # Dokumentasi proyek
```

---

## 📸 Tampilan Aplikasi

### Halaman Login
Halaman autentikasi dengan username dan password. Mendukung tombol Enter untuk submit langsung.

### Dashboard
Menampilkan ringkasan total kamar, penghuni aktif, kamar kosong, dan daftar penghuni yang belum membayar di bulan berjalan.

### Manajemen Pembayaran
Ibu kost dapat menandai status pembayaran setiap penghuni (lunas/belum) untuk periode bulan dan tahun tertentu.

---

<div align="center">

Dibuat dengan ❤️ oleh **Kelompok 5** — Informatika UIN Siber Syekh Nurjati Cirebon

</div>
