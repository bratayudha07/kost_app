"""
app.py — Aplikasi Streamlit Manajemen Kost
Jalankan dengan: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Any
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import database as db

# ─── Konfigurasi Halaman ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Manajemen Kost",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 1.5rem;}
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)


# ─── Init ─────────────────────────────────────────────────────────────────────

db.init_db()

# Session state defaults
for key, val in [("logged_in", False), ("username", ""),
                 ("page", "Dashboard"), ("session_token", "")]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── Cek session token dari query params (persist login setelah reload) ────────
if not st.session_state.logged_in:
    params = st.query_params
    token  = params.get("t", "")
    if token and db.check_session(token):
        st.session_state.logged_in    = True
        st.session_state.session_token = token
        # Ambil username dari DB (satu-satunya user)
        st.session_state.username = "admin"


# ─── Helper ───────────────────────────────────────────────────────────────────

BULAN = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

def nama_bulan(n: int) -> str:
    return BULAN[n] if 1 <= n <= 12 else str(n)

def fmt_rupiah(n: Any) -> str:
    return f"Rp {int(n):,}".replace(",", ".")

def go(page: str) -> None:
    st.session_state.page = page

def safe_str(val: str | None) -> str:
    return val if val is not None else ""

def rename_df(df: Any, mapping: dict[str, str]) -> pd.DataFrame:
    return pd.DataFrame(df).rename(columns=mapping)  # type: ignore[call-overload]


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN LOGIN
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_login() -> None:
    col_l, col_m, col_r = st.columns([1.2, 1, 1.2])
    with col_m:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🏠 Manajemen Kost")
        st.markdown("---")
        st.markdown("### 🔐 Login")

        # Pakai st.form agar Enter langsung submit
        with st.form("form_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Masuk", use_container_width=True, type="primary")

        if submitted:
            if db.check_login(safe_str(username), safe_str(password)):
                token = db.create_session()
                st.session_state.logged_in     = True
                st.session_state.username      = safe_str(username)
                st.session_state.session_token = token
                # Simpan token di URL agar persist setelah reload
                st.query_params["t"] = token
                st.rerun()
            else:
                st.error("❌ Username atau password salah!")


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGASI
# ═══════════════════════════════════════════════════════════════════════════════

def sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🏠 Kost Manager")
        st.caption(f"Halo, **{st.session_state.username}**!")
        st.markdown("---")

        menu = {
            "📊 Dashboard":           "Dashboard",
            "🏠 Manajemen Kamar":     "Kamar",
            "👥 Manajemen Penghuni":  "Penghuni",
            "💰 Pembayaran":          "Pembayaran",
            "📋 Riwayat":             "Riwayat",
            "🏚️ Kamar Kosong":       "KamarKosong",
            "📤 Export Data":         "Export",
            "⚙️ Pengaturan":          "Settings",
        }

        for label, key in menu.items():
            active   = st.session_state.page == key
            btn_type = "primary" if active else "secondary"
            if st.button(label, width="stretch", key=f"nav_{key}", type=btn_type):
                go(key)
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", width="stretch"):
            db.clear_session()
            st.query_params.clear()
            st.session_state.logged_in     = False
            st.session_state.session_token = ""
            st.session_state.page          = "Dashboard"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_dashboard() -> None:
    st.markdown("## 📊 Dashboard")
    st.markdown("---")

    now = datetime.now()
    bln = now.month
    thn = now.year

    total_kamar    = db.get_all_kamar()
    penghuni_aktif = db.get_penghuni_aktif()
    kamar_kosong   = db.get_kamar_kosong()
    belum_bayar    = db.get_belum_bayar(bln, thn)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏠 Total Kamar",    len(total_kamar))
    c2.metric("👥 Penghuni Aktif", len(penghuni_aktif))
    c3.metric("🏚️ Kamar Kosong",  len(kamar_kosong))
    c4.metric(f"❌ Belum Bayar ({nama_bulan(bln)})", len(belum_bayar))

    st.markdown("---")
    st.markdown(f"### ⚠️ Belum Bayar — {nama_bulan(bln)} {thn}")

    if belum_bayar:
        df = pd.DataFrame([dict(r) for r in belum_bayar])
        df = rename_df(df, {"nama": "Nama", "nomor_kamar": "Kamar", "no_hp": "No. HP"})
        st.dataframe(df[["Kamar", "Nama", "No. HP"]], width="stretch", hide_index=True)
    else:
        st.success(f"🎉 Semua penghuni sudah bayar bulan {nama_bulan(bln)}!")

    st.markdown("---")
    st.markdown("### 🏠 Ringkasan Kamar")
    if total_kamar:
        data_kamar = []
        for k in total_kamar:
            ph = [p for p in penghuni_aktif if p["kamar_id"] == k["id"]]
            data_kamar.append({
                "Kamar"       : k["nomor_kamar"],
                "Harga Sewa"  : fmt_rupiah(k["harga_sewa"]),
                "Jml Penghuni": len(ph),
                "Status"      : "🟢 Terisi" if ph else "⚪ Kosong",
            })
        st.dataframe(pd.DataFrame(data_kamar), width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN KAMAR
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_kamar() -> None:
    st.markdown("## 🏠 Manajemen Kamar")
    st.markdown("---")

    tab_daftar, tab_tambah = st.tabs(["📋 Daftar Kamar", "➕ Tambah Kamar"])

    with tab_daftar:
        kamar_list = db.get_all_kamar()
        if not kamar_list:
            st.info("Belum ada kamar. Silakan tambah terlebih dahulu.")
        else:
            df = pd.DataFrame([dict(r) for r in kamar_list])
            df["Harga Sewa"] = df["harga_sewa"].apply(fmt_rupiah)  # type: ignore[union-attr]
            st.dataframe(
                rename_df(df[["nomor_kamar", "Harga Sewa"]], {"nomor_kamar": "Nomor Kamar"}),
                width="stretch", hide_index=True
            )

            st.markdown("### ✏️ Edit / Hapus Kamar")
            opts     = {f"Kamar {r['nomor_kamar']}": r["id"] for r in kamar_list}
            sel      = st.selectbox("Pilih kamar", list(opts.keys()))
            k_id     = opts[safe_str(sel)]
            kd       = next(r for r in kamar_list if r["id"] == k_id)

            col1, col2 = st.columns(2)
            new_nomor  = col1.text_input("Nomor Kamar", value=str(kd["nomor_kamar"]))
            new_harga  = col2.number_input("Harga Sewa (Rp)", value=int(kd["harga_sewa"]), step=50_000)

            col_a, col_b = st.columns(2)
            if col_a.button("💾 Simpan Perubahan", type="primary"):
                try:
                    db.update_kamar(k_id, safe_str(new_nomor), int(new_harga))
                    st.success("Kamar berhasil diperbarui!")
                    st.rerun()
                except Exception:
                    st.error("Gagal — nomor kamar mungkin sudah dipakai.")

            if col_b.button("🗑️ Hapus Kamar"):
                try:
                    db.delete_kamar(k_id)
                    st.success("Kamar berhasil dihapus.")
                    st.rerun()
                except Exception:
                    st.error("Tidak bisa hapus — kamar masih memiliki penghuni.")

    with tab_tambah:
        with st.form("form_tambah_kamar", clear_on_submit=True):
            nomor = st.text_input("Nomor Kamar (contoh: 101, A1, B2)")
            harga = st.number_input("Harga Sewa per Bulan (Rp)", min_value=0, step=50_000)
            if st.form_submit_button("➕ Tambah Kamar", type="primary"):
                nomor_val = safe_str(nomor).strip()
                if nomor_val:
                    try:
                        db.add_kamar(nomor_val, int(harga))
                        st.success(f"Kamar **{nomor_val}** berhasil ditambahkan!")
                        st.rerun()
                    except Exception:
                        st.error("Nomor kamar sudah ada.")
                else:
                    st.warning("Nomor kamar tidak boleh kosong.")


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN PENGHUNI
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_penghuni() -> None:
    st.markdown("## 👥 Manajemen Penghuni")
    st.markdown("---")

    tab_daftar, tab_tambah, tab_edit, tab_nonaktif, tab_hapus = st.tabs([
        "📋 Daftar", "➕ Tambah", "✏️ Edit", "🚪 Nonaktifkan", "🗑️ Hapus"
    ])

    kamar_list = db.get_all_kamar()

    # ── Daftar ────────────────────────────────────────────────────────────────
    with tab_daftar:
        penghuni_all = db.get_all_penghuni()
        if not penghuni_all:
            st.info("Belum ada data penghuni.")
        else:
            filter_status = st.radio("Tampilkan", ["Semua", "Aktif", "Nonaktif"], horizontal=True)
            df = pd.DataFrame([dict(r) for r in penghuni_all])
            if filter_status == "Aktif":
                df = df[df["status"] == "aktif"]
            elif filter_status == "Nonaktif":
                df = df[df["status"] == "nonaktif"]

            df = df.copy()
            df["Status"] = pd.Series(df["status"]).replace(  # type: ignore[arg-type]
                {"aktif": "🟢 Aktif", "nonaktif": "🔴 Nonaktif"}
            )
            df = rename_df(df, {
                "nomor_kamar"   : "Kamar",   "nama"          : "Nama",
                "no_hp"         : "No. HP",  "no_rekening"   : "No. Rekening",
                "alamat"        : "Alamat",  "tanggal_masuk" : "Tgl Masuk",
                "tanggal_keluar": "Tgl Keluar",
            })
            cols = ["Kamar", "Nama", "No. HP", "No. Rekening",
                    "Alamat", "Tgl Masuk", "Tgl Keluar", "Status"]
            st.dataframe(df[cols], width="stretch", hide_index=True)

    # ── Tambah ────────────────────────────────────────────────────────────────
    with tab_tambah:
        if not kamar_list:
            st.warning("⚠️ Tambah kamar terlebih dahulu.")
        else:
            with st.form("form_tambah_penghuni", clear_on_submit=True):
                kamar_opts = {f"Kamar {r['nomor_kamar']}": r["id"] for r in kamar_list}
                sel_kamar  = st.selectbox("Kamar", list(kamar_opts.keys()))
                nama       = st.text_input("Nama Lengkap")
                col1, col2 = st.columns(2)
                no_hp      = col1.text_input("No. HP")
                no_rek     = col2.text_input("No. Rekening")
                alamat     = st.text_area("Alamat")
                tgl_masuk  = st.date_input("Tanggal Masuk", value=date.today())

                if st.form_submit_button("➕ Tambah Penghuni", type="primary"):
                    nama_val = safe_str(nama).strip()
                    if nama_val:
                        db.add_penghuni(
                            kamar_opts[safe_str(sel_kamar)], nama_val,
                            safe_str(alamat), safe_str(no_hp), safe_str(no_rek),
                            tgl_masuk if isinstance(tgl_masuk, date) else date.today(),
                        )
                        st.success(f"Penghuni **{nama_val}** berhasil ditambahkan!")
                        st.rerun()
                    else:
                        st.warning("Nama tidak boleh kosong.")

    # ── Edit ──────────────────────────────────────────────────────────────────
    with tab_edit:
        penghuni_aktif = db.get_penghuni_aktif()
        if not penghuni_aktif:
            st.info("Tidak ada penghuni aktif yang bisa diedit.")
        else:
            opts  = {f"{r['nama']} — Kamar {r['nomor_kamar']}": r["id"] for r in penghuni_aktif}
            sel   = st.selectbox("Pilih Penghuni", list(opts.keys()), key="edit_sel")
            p_id  = opts[safe_str(sel)]
            pd_   = next(r for r in penghuni_aktif if r["id"] == p_id)

            kamar_opts = {f"Kamar {r['nomor_kamar']}": r["id"] for r in kamar_list}
            cur_kamar  = f"Kamar {pd_['nomor_kamar']}"
            kamar_keys = list(kamar_opts.keys())
            idx_kamar  = kamar_keys.index(cur_kamar) if cur_kamar in kamar_keys else 0

            with st.form("form_edit_penghuni"):
                sel_kamar = st.selectbox("Kamar", kamar_keys, index=idx_kamar)
                nama      = st.text_input("Nama Lengkap", value=str(pd_["nama"]))
                col1, col2 = st.columns(2)
                no_hp     = col1.text_input("No. HP", value=str(pd_["no_hp"] or ""))
                no_rek    = col2.text_input("No. Rekening", value=str(pd_["no_rekening"] or ""))
                alamat    = st.text_area("Alamat", value=str(pd_["alamat"] or ""))
                tgl_masuk = st.date_input(
                    "Tanggal Masuk",
                    value=date.fromisoformat(str(pd_["tanggal_masuk"]))
                )
                if st.form_submit_button("💾 Simpan Perubahan", type="primary"):
                    nama_val = safe_str(nama).strip()
                    if nama_val:
                        db.update_penghuni(
                            p_id, kamar_opts[safe_str(sel_kamar)], nama_val,
                            safe_str(alamat), safe_str(no_hp), safe_str(no_rek),
                            tgl_masuk if isinstance(tgl_masuk, date) else date.today(),
                        )
                        st.success("Data penghuni berhasil diperbarui!")
                        st.rerun()
                    else:
                        st.warning("Nama tidak boleh kosong.")

    # ── Nonaktifkan ───────────────────────────────────────────────────────────
    with tab_nonaktif:
        penghuni_aktif = db.get_penghuni_aktif()
        if not penghuni_aktif:
            st.info("Tidak ada penghuni aktif.")
        else:
            st.info("💡 Data penghuni tetap tersimpan sebagai riwayat setelah dinonaktifkan.")
            opts       = {f"{r['nama']} — Kamar {r['nomor_kamar']}": r["id"] for r in penghuni_aktif}
            sel        = st.selectbox("Pilih Penghuni", list(opts.keys()), key="nonaktif_sel")
            tgl_keluar = st.date_input("Tanggal Keluar", value=date.today())

            if st.button("🚪 Nonaktifkan Penghuni", type="primary"):
                tgl_val = tgl_keluar if isinstance(tgl_keluar, date) else date.today()
                db.nonaktifkan_penghuni(opts[safe_str(sel)], str(tgl_val))
                st.success(f"**{sel}** telah dinonaktifkan.")
                st.rerun()

    # ── Hapus ─────────────────────────────────────────────────────────────────
    with tab_hapus:
        semua = db.get_all_penghuni()
        if not semua:
            st.info("Belum ada data penghuni.")
        else:
            st.warning("⚠️ Data penghuni dan seluruh riwayat pembayarannya akan **dihapus permanen**.")
            opts = {f"{r['nama']} — Kamar {r['nomor_kamar']} ({r['status']})": r["id"] for r in semua}
            sel  = st.selectbox("Pilih Penghuni", list(opts.keys()), key="hapus_sel")

            konfirmasi = st.checkbox(f"Ya, saya yakin ingin menghapus **{sel}**")
            if st.button("🗑️ Hapus Permanen", type="primary", disabled=not konfirmasi):
                db.delete_penghuni(opts[safe_str(sel)])
                st.success("Penghuni berhasil dihapus.")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN PEMBAYARAN
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_pembayaran() -> None:
    st.markdown("## 💰 Pembayaran Bulanan")
    st.markdown("---")

    col1, col2 = st.columns(2)
    bln = int(col1.selectbox("Bulan", range(1, 13),
                              index=datetime.now().month - 1, format_func=nama_bulan))
    thn = int(col2.number_input("Tahun", min_value=2020, max_value=2030,
                                 value=datetime.now().year))
    st.markdown("---")

    penghuni_aktif = db.get_penghuni_aktif()
    if not penghuni_aktif:
        st.info("Belum ada penghuni aktif.")
        return

    existing   = db.get_pembayaran(bln, thn)
    status_map = {r["penghuni_id"]: r["status"] for r in existing}

    sudah = sum(1 for s in status_map.values() if s == "lunas")
    belum = len(penghuni_aktif) - sudah

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Penghuni Aktif", len(penghuni_aktif))
    m2.metric("✅ Sudah Bayar", sudah)
    m3.metric("❌ Belum Bayar", belum)

    st.markdown(f"### Status Pembayaran — {nama_bulan(bln)} {thn}")
    st.markdown("---")

    for p in penghuni_aktif:
        status     = status_map.get(p["id"], "belum")
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.markdown(f"**{p['nama']}**  \nKamar {p['nomor_kamar']}")

        if status == "lunas":
            c2.success("✅ Lunas")
            if c3.button("Batalkan", key=f"batal_{p['id']}_{bln}_{thn}"):
                db.upsert_pembayaran(p["id"], bln, thn, "belum")
                st.rerun()
        else:
            c2.error("❌ Belum")
            if c3.button("Tandai Lunas", key=f"lunas_{p['id']}_{bln}_{thn}", type="primary"):
                db.upsert_pembayaran(p["id"], bln, thn, "lunas")
                st.rerun()
        st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN RIWAYAT
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_riwayat() -> None:
    st.markdown("## 📋 Riwayat")
    st.markdown("---")

    tab_bayar, tab_kamar = st.tabs([
        "💳 Riwayat Pembayaran per Penghuni",
        "🏠 Riwayat Penghuni per Kamar",
    ])

    with tab_bayar:
        penghuni_all = db.get_all_penghuni()
        if not penghuni_all:
            st.info("Belum ada data penghuni.")
        else:
            opts = {f"{r['nama']} — Kamar {r['nomor_kamar']} ({r['status']})": r["id"]
                    for r in penghuni_all}
            sel     = st.selectbox("Pilih Penghuni", list(opts.keys()))
            p_id    = opts[safe_str(sel)]
            riwayat = db.get_riwayat_pembayaran(p_id)

            if riwayat:
                df = pd.DataFrame([dict(r) for r in riwayat])
                df["Periode"] = df["bulan"].apply(nama_bulan) + " " + df["tahun"].astype(str)  # type: ignore[union-attr]
                df["Status"]  = pd.Series(df["status"]).replace(  # type: ignore[arg-type]
                    {"lunas": "✅ Lunas", "belum": "❌ Belum"}
                )
                lunas = int((df["status"] == "lunas").sum())
                belum = int((df["status"] == "belum").sum())
                c1, c2 = st.columns(2)
                c1.metric("✅ Total Lunas", lunas)
                c2.metric("❌ Total Belum", belum)
                st.dataframe(df[["Periode", "Status"]], width="stretch", hide_index=True)
            else:
                st.info("Belum ada riwayat pembayaran untuk penghuni ini.")

    with tab_kamar:
        kamar_list = db.get_all_kamar()
        if not kamar_list:
            st.info("Belum ada data kamar.")
        else:
            opts = {f"Kamar {r['nomor_kamar']}": r["id"] for r in kamar_list}
            sel  = st.selectbox("Pilih Kamar", list(opts.keys()), key="riwayat_kamar")
            k_id = opts[safe_str(sel)]
            rows = db.get_penghuni_by_kamar(k_id)

            if rows:
                df = pd.DataFrame([dict(r) for r in rows])
                df["Status"] = pd.Series(df["status"]).replace(  # type: ignore[arg-type]
                    {"aktif": "🟢 Aktif", "nonaktif": "🔴 Nonaktif"}
                )
                df = rename_df(df, {
                    "nama": "Nama", "no_hp": "No. HP",
                    "tanggal_masuk": "Tgl Masuk", "tanggal_keluar": "Tgl Keluar",
                })
                st.dataframe(df[["Nama", "No. HP", "Tgl Masuk", "Tgl Keluar", "Status"]],
                             width="stretch", hide_index=True)
            else:
                st.info("Kamar ini belum pernah dihuni.")


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN KAMAR KOSONG
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_kamar_kosong() -> None:
    st.markdown("## 🏚️ Kamar Kosong")
    st.markdown("---")

    total  = db.get_all_kamar()
    kosong = db.get_kamar_kosong()
    terisi = len(total) - len(kosong)

    c1, c2, c3 = st.columns(3)
    c1.metric("🏠 Total Kamar", len(total))
    c2.metric("🟢 Terisi",      terisi)
    c3.metric("⚪ Kosong",       len(kosong))

    st.markdown("---")
    if kosong:
        df = pd.DataFrame([dict(r) for r in kosong])
        df["Harga Sewa"] = df["harga_sewa"].apply(fmt_rupiah)  # type: ignore[union-attr]
        st.dataframe(
            rename_df(df[["nomor_kamar", "Harga Sewa"]], {"nomor_kamar": "Nomor Kamar"}),
            width="stretch", hide_index=True
        )
    else:
        st.success("🎉 Semua kamar sedang terisi!")


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_export() -> None:
    st.markdown("## 📤 Export Data")
    st.markdown("---")

    tab_penghuni, tab_bulanan, tab_rekap = st.tabs([
        "👥 Data Penghuni", "💰 Pembayaran Bulanan", "📊 Rekap Lengkap"
    ])

    with tab_penghuni:
        rows = db.get_all_penghuni()
        if rows:
            df = rename_df(pd.DataFrame([dict(r) for r in rows]), {
                "nomor_kamar": "Kamar", "nama": "Nama", "alamat": "Alamat",
                "no_hp": "No HP", "no_rekening": "No Rekening",
                "tanggal_masuk": "Tgl Masuk", "tanggal_keluar": "Tgl Keluar", "status": "Status",
            })
            cols = ["Kamar", "Nama", "No HP", "No Rekening", "Alamat", "Tgl Masuk", "Tgl Keluar", "Status"]
            st.dataframe(df[cols], width="stretch", hide_index=True)
            st.download_button("⬇️ Download CSV", df[cols].to_csv(index=False).encode("utf-8"),
                               "penghuni.csv", "text/csv", width="stretch")
        else:
            st.info("Belum ada data penghuni.")

    with tab_bulanan:
        col1, col2 = st.columns(2)
        bln = int(col1.selectbox("Bulan", range(1, 13), index=datetime.now().month - 1,
                                  format_func=nama_bulan, key="exp_bln"))
        thn = int(col2.number_input("Tahun", min_value=2020, max_value=2030,
                                     value=datetime.now().year, key="exp_thn"))
        rows = db.get_pembayaran(bln, thn)
        if rows:
            df = pd.DataFrame([dict(r) for r in rows])
            df["Periode"] = f"{nama_bulan(bln)} {thn}"
            df["Status"]  = pd.Series(df["status"]).replace({"lunas": "Lunas", "belum": "Belum"})  # type: ignore[arg-type]
            df = rename_df(df, {"nama": "Nama", "nomor_kamar": "Kamar"})
            cols = ["Periode", "Kamar", "Nama", "Status"]
            st.dataframe(df[cols], width="stretch", hide_index=True)
            st.download_button(f"⬇️ Download CSV — {nama_bulan(bln)} {thn}",
                               df[cols].to_csv(index=False).encode("utf-8"),
                               f"pembayaran_{bln}_{thn}.csv", "text/csv", width="stretch")
        else:
            st.info("Belum ada data pembayaran untuk periode ini.")

    with tab_rekap:
        rows = db.get_semua_pembayaran()
        if rows:
            df = pd.DataFrame([dict(r) for r in rows])
            df["Bulan"]  = df["bulan"].apply(nama_bulan)  # type: ignore[union-attr]
            df["Status"] = pd.Series(df["status"]).replace({"lunas": "Lunas", "belum": "Belum"})  # type: ignore[arg-type]
            df = rename_df(df, {"tahun": "Tahun", "nomor_kamar": "Kamar", "nama": "Nama"})
            cols = ["Tahun", "Bulan", "Kamar", "Nama", "Status"]
            st.dataframe(df[cols], width="stretch", hide_index=True)
            st.download_button("⬇️ Download CSV — Rekap Lengkap",
                               df[cols].to_csv(index=False).encode("utf-8"),
                               "rekap_pembayaran.csv", "text/csv", width="stretch")
        else:
            st.info("Belum ada data pembayaran sama sekali.")


# ═══════════════════════════════════════════════════════════════════════════════
# HALAMAN SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

def halaman_settings() -> None:
    st.markdown("## ⚙️ Pengaturan Akun")
    st.markdown("---")

    tab_pw, tab_user = st.tabs(["🔑 Ganti Password", "👤 Ganti Username"])

    # ── Ganti Password ────────────────────────────────────────────────────────
    with tab_pw:
        with st.form("form_ganti_pw"):
            pw_lama  = st.text_input("Password Lama", type="password")
            pw_baru  = st.text_input("Password Baru", type="password")
            pw_ulang = st.text_input("Ulangi Password Baru", type="password")

            if st.form_submit_button("🔑 Simpan Password", type="primary"):
                if not db.check_login(st.session_state.username, safe_str(pw_lama)):
                    st.error("❌ Password lama salah.")
                elif safe_str(pw_baru) != safe_str(pw_ulang):
                    st.error("❌ Password baru tidak cocok.")
                elif len(safe_str(pw_baru)) < 6:
                    st.warning("⚠️ Password minimal 6 karakter.")
                else:
                    db.change_password(st.session_state.username, safe_str(pw_baru))
                    st.success("✅ Password berhasil diubah!")

    # ── Ganti Username ────────────────────────────────────────────────────────
    with tab_user:
        with st.form("form_ganti_user"):
            user_baru = st.text_input("Username Baru")
            pw_konfirm = st.text_input("Konfirmasi Password", type="password")

            if st.form_submit_button("👤 Simpan Username", type="primary"):
                user_val = safe_str(user_baru).strip()
                if not db.check_login(st.session_state.username, safe_str(pw_konfirm)):
                    st.error("❌ Password salah.")
                elif not user_val:
                    st.warning("⚠️ Username tidak boleh kosong.")
                else:
                    try:
                        db.change_username(st.session_state.username, user_val)
                        st.session_state.username = user_val
                        st.success(f"✅ Username berhasil diubah ke **{user_val}**!")
                        st.rerun()
                    except Exception:
                        st.error("❌ Username sudah dipakai.")


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER UTAMA
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    if not st.session_state.logged_in:
        halaman_login()
        return

    sidebar()

    router = {
        "Dashboard"  : halaman_dashboard,
        "Kamar"      : halaman_kamar,
        "Penghuni"   : halaman_penghuni,
        "Pembayaran" : halaman_pembayaran,
        "Riwayat"    : halaman_riwayat,
        "KamarKosong": halaman_kamar_kosong,
        "Export"     : halaman_export,
        "Settings"   : halaman_settings,
    }

    halaman = router.get(st.session_state.page, halaman_dashboard)
    halaman()


if __name__ == "__main__":
    main()
