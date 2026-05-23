"""
database.py — Semua fungsi query untuk database kost.
Menggunakan SQLite agar tidak perlu install server terpisah.

Fix v2: semua fungsi pakai context manager (with get_conn())
agar koneksi SELALU ditutup meski ada exception — tidak ada lagi
database locked akibat connection leak.
"""

import sqlite3
import hashlib
import os
from contextlib import contextmanager

DB_PATH = "kost.db"
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


# ─── Koneksi & Inisialisasi ───────────────────────────────────────────────────

@contextmanager
def get_conn():
    """Context manager koneksi — otomatis tutup meski ada exception."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Buat tabel dari schema.sql, lalu seed user default jika belum ada."""
    with get_conn() as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
        hashed = _hash("kelompok5")
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            ("admin", hashed)
        )


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ─── Auth ─────────────────────────────────────────────────────────────────────

def check_login(username: str, password: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ? AND password = ?",
            (username, _hash(password))
        ).fetchone()
    return row is not None


def change_password(username: str, new_password: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (_hash(new_password), username)
        )


# ─── Kamar ────────────────────────────────────────────────────────────────────

def get_all_kamar():
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM kamar ORDER BY nomor_kamar"
        ).fetchall()


def add_kamar(nomor_kamar: str, harga_sewa: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO kamar (nomor_kamar, harga_sewa) VALUES (?, ?)",
            (nomor_kamar, harga_sewa)
        )


def update_kamar(kamar_id: int, nomor_kamar: str, harga_sewa: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE kamar SET nomor_kamar = ?, harga_sewa = ? WHERE id = ?",
            (nomor_kamar, harga_sewa, kamar_id)
        )


def delete_kamar(kamar_id: int):
    """Hapus kamar — gagal jika masih ada penghuni (FK constraint)."""
    with get_conn() as conn:
        conn.execute("DELETE FROM kamar WHERE id = ?", (kamar_id,))


def get_kamar_kosong():
    """Kamar yang tidak punya penghuni berstatus aktif."""
    with get_conn() as conn:
        return conn.execute("""
            SELECT k.*
            FROM kamar k
            WHERE NOT EXISTS (
                SELECT 1 FROM penghuni p
                WHERE p.kamar_id = k.id AND p.status = 'aktif'
            )
            ORDER BY k.nomor_kamar
        """).fetchall()


# ─── Penghuni ─────────────────────────────────────────────────────────────────

def get_all_penghuni():
    with get_conn() as conn:
        return conn.execute("""
            SELECT p.*, k.nomor_kamar
            FROM penghuni p
            JOIN kamar k ON p.kamar_id = k.id
            ORDER BY k.nomor_kamar, p.nama
        """).fetchall()


def get_penghuni_aktif():
    with get_conn() as conn:
        return conn.execute("""
            SELECT p.*, k.nomor_kamar
            FROM penghuni p
            JOIN kamar k ON p.kamar_id = k.id
            WHERE p.status = 'aktif'
            ORDER BY k.nomor_kamar, p.nama
        """).fetchall()


def get_penghuni_by_kamar(kamar_id: int):
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM penghuni
            WHERE kamar_id = ?
            ORDER BY tanggal_masuk
        """, (kamar_id,)).fetchall()


def add_penghuni(kamar_id, nama, alamat, no_hp, no_rekening, tanggal_masuk):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO penghuni
                (kamar_id, nama, alamat, no_hp, no_rekening, tanggal_masuk, status)
            VALUES (?, ?, ?, ?, ?, ?, 'aktif')
        """, (kamar_id, nama, alamat, no_hp, no_rekening, str(tanggal_masuk)))


def update_penghuni(penghuni_id, kamar_id, nama, alamat, no_hp, no_rekening, tanggal_masuk):
    with get_conn() as conn:
        conn.execute("""
            UPDATE penghuni
            SET kamar_id = ?, nama = ?, alamat = ?,
                no_hp = ?, no_rekening = ?, tanggal_masuk = ?
            WHERE id = ?
        """, (kamar_id, nama, alamat, no_hp, no_rekening, str(tanggal_masuk), penghuni_id))


def nonaktifkan_penghuni(penghuni_id: int, tanggal_keluar: str):
    with get_conn() as conn:
        conn.execute("""
            UPDATE penghuni
            SET status = 'nonaktif', tanggal_keluar = ?
            WHERE id = ?
        """, (str(tanggal_keluar), penghuni_id))


# ─── Pembayaran ───────────────────────────────────────────────────────────────

def get_pembayaran(bulan: int, tahun: int):
    with get_conn() as conn:
        return conn.execute("""
            SELECT pb.*, p.nama, k.nomor_kamar
            FROM pembayaran pb
            JOIN penghuni p ON pb.penghuni_id = p.id
            JOIN kamar k ON p.kamar_id = k.id
            WHERE pb.bulan = ? AND pb.tahun = ?
            ORDER BY k.nomor_kamar, p.nama
        """, (bulan, tahun)).fetchall()


def upsert_pembayaran(penghuni_id: int, bulan: int, tahun: int, status: str):
    """Insert jika belum ada, update jika sudah ada."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO pembayaran (penghuni_id, bulan, tahun, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(penghuni_id, bulan, tahun)
            DO UPDATE SET status = excluded.status
        """, (penghuni_id, bulan, tahun, status))


def get_belum_bayar(bulan: int, tahun: int):
    """Penghuni aktif yang belum bayar — termasuk yang belum punya record."""
    with get_conn() as conn:
        return conn.execute("""
            SELECT p.id, p.nama, k.nomor_kamar, p.no_hp
            FROM penghuni p
            JOIN kamar k ON p.kamar_id = k.id
            WHERE p.status = 'aktif'
              AND (
                  NOT EXISTS (
                      SELECT 1 FROM pembayaran pb
                      WHERE pb.penghuni_id = p.id
                        AND pb.bulan = ? AND pb.tahun = ?
                  )
                  OR EXISTS (
                      SELECT 1 FROM pembayaran pb
                      WHERE pb.penghuni_id = p.id
                        AND pb.bulan = ? AND pb.tahun = ?
                        AND pb.status = 'belum'
                  )
              )
            ORDER BY k.nomor_kamar, p.nama
        """, (bulan, tahun, bulan, tahun)).fetchall()


def get_riwayat_pembayaran(penghuni_id: int):
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM pembayaran
            WHERE penghuni_id = ?
            ORDER BY tahun DESC, bulan DESC
        """, (penghuni_id,)).fetchall()


def get_semua_pembayaran():
    with get_conn() as conn:
        return conn.execute("""
            SELECT pb.tahun, pb.bulan, k.nomor_kamar, p.nama, pb.status
            FROM pembayaran pb
            JOIN penghuni p ON pb.penghuni_id = p.id
            JOIN kamar k ON p.kamar_id = k.id
            ORDER BY pb.tahun DESC, pb.bulan DESC, k.nomor_kamar
        """).fetchall()
