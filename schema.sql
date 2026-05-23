-- ============================================
-- Schema Database Manajemen Kost
-- ============================================

-- Tabel login ibu kost
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL  -- disimpan sebagai SHA-256 hash
);

-- Tabel kamar
CREATE TABLE IF NOT EXISTS kamar (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor_kamar  TEXT    NOT NULL UNIQUE,
    harga_sewa   INTEGER NOT NULL DEFAULT 0
);

-- Tabel penghuni (aktif maupun nonaktif untuk riwayat)
CREATE TABLE IF NOT EXISTS penghuni (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    kamar_id       INTEGER NOT NULL,
    nama           TEXT    NOT NULL,
    alamat         TEXT,
    no_hp          TEXT,
    no_rekening    TEXT,
    tanggal_masuk  TEXT    NOT NULL,  -- format: YYYY-MM-DD
    tanggal_keluar TEXT,              -- NULL = masih aktif
    status         TEXT    NOT NULL DEFAULT 'aktif'
                           CHECK(status IN ('aktif', 'nonaktif')),
    FOREIGN KEY (kamar_id) REFERENCES kamar(id)
);

-- Tabel pembayaran bulanan
-- Satu record = satu penghuni, satu bulan, satu tahun
CREATE TABLE IF NOT EXISTS pembayaran (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    penghuni_id  INTEGER NOT NULL,
    bulan        INTEGER NOT NULL CHECK(bulan BETWEEN 1 AND 12),
    tahun        INTEGER NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'belum'
                         CHECK(status IN ('lunas', 'belum')),
    UNIQUE(penghuni_id, bulan, tahun),  -- tidak boleh duplikat
    FOREIGN KEY (penghuni_id) REFERENCES penghuni(id)
);
