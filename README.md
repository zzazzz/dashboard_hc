# HC Analytics Case #1 — Regretted Attrition Dashboard

Dashboard Streamlit untuk kasus *"Regretted Attrition di Cabang Wilayah Timur"* — dibangun
langsung dari data kasus (`data/hc_data.xlsx`, dianonimkan), bukan data contoh.

## Menjalankan secara lokal

```bash
pip install -r requirements.txt
python build_cache.py     # sekali saja, atau tiap data mentah diperbarui
streamlit run app.py
```

## Catatan performa

Versi awal butuh ~5,9 detik untuk cold start. Hasil profiling:

| Bagian | Waktu |
|---|---|
| `import streamlit` | 1,58 s |
| Baca 8 sheet dari `.xlsx` | 3,45 s (sheet Data Kompensasi 34.916 baris = 2,79 s sendiri) |
| `import plotly` + `pandas` | 0,47 s |

Biang keroknya baca `.xlsx`: formatnya ZIP berisi XML, jadi pandas harus unzip
lalu parsing per sel. `build_cache.py` mengonversinya ke Parquet (kolom biner,
tipe data sudah pasti) — 1,6 MB jadi 281 KB total, dan waktu baca turun dari
**3,45 s → 0,14 s**. Cold start sekarang **1,57 detik**.

Kalau folder `data/parquet/` tidak ada, `app.py` otomatis jatuh balik membaca
`.xlsx` (sudah dites), jadi aplikasi tetap jalan — hanya lebih lambat.

Rerun setelah ganti filter memang sudah cepat sejak awal (~0,45 s) karena
`load_data()` dibungkus `@st.cache_data`, jadi data tidak dibaca ulang.

**Kalau lambatnya terjadi di Streamlit Community Cloud**, penyebabnya beda lagi
dan di luar kode: app gratis di-*sleep* setelah tidak dipakai, dan saat
dibangunkan container harus boot + `pip install` seluruh `requirements.txt`
dulu (bisa 30-60 detik). Yang membantu di sini: menjaga `requirements.txt`
tetap ramping (tanpa scikit-learn dsb. yang memang tidak dipakai app ini) dan
mem-pin versinya.

Sudah diuji end-to-end di sandbox ini dengan dua cara:
1. `streamlit.testing.v1.AppTest` — menjalankan seluruh skrip, mengganti filter sidebar,
   dan memastikan tidak ada exception di setiap tab.
2. Server headless sungguhan (`streamlit run ... --server.headless true`) yang dites dengan
   `curl` dan mengembalikan `HTTP 200` — jadi jalurnya sama seperti saat nanti di-deploy.

## Struktur

```
app.py                     # seluruh logika dashboard (load data, filter, 5 tab)
data/hc_data.xlsx          # workbook kasus (8 sheet: Data Cabang, Data Karyawan, Reason Out, dst.)
.streamlit/config.toml     # tema dark + pengaturan server
requirements.txt
```

Tab **Ringkasan** sengaja dibatasi 6 visual di satu layar (KPI + 6 chart) agar langsung sesuai
deliverable kasus ("dashboard sederhana, maksimal 6 visual, satu layar"). Empat tab lain
(Regional & Cabang, Kohort & Alasan, Kompensasi & Engagement, Rekomendasi) adalah *deep dive*
tambahan untuk eksplorasi dan bahan sesi tanya-jawab — silakan hapus tab-tab ini kalau untuk
submission maunya benar-benar satu layar saja.

## Soal "jangan upload data ke production / pakai API"

Data kasus ini adalah **dataset kasus yang tetap** (dummy, sudah dianonimkan) — bukan indikator
publik yang punya API resmi seperti data BPS pada dashboard referensi. Karena itu tidak ada
API yang bisa dipanggil untuk menggantikannya; pilihan yang wajar adalah membaca file lokal
sekali lalu di-cache (`@st.cache_data`), seperti yang dilakukan `load_data()` di `app.py`.

Kalau tujuannya supaya file `.xlsx` **tidak ikut ter-commit ke repo publik**, ada dua opsi
tanpa mengubah arsitektur aplikasi (cukup ganti isi `load_data()`):
- **Streamlit secrets + cloud storage**: upload `hc_data.xlsx` ke Google Drive/S3 sebagai
  private object, simpan URL/credential di *Secrets* Streamlit Cloud, lalu `pd.read_excel(url_or_signed_link)`.
  Data tetap tidak ada di repo, hanya diambil saat runtime.
  Streamlit
- **Private repo / private data folder**: kalau repo GitHub-nya sudah private, menyimpan
  `data/hc_data.xlsx` langsung di repo (seperti struktur saat ini) sudah aman dan paling
  sederhana — inilah yang dipakai di paket ini.

Kalau nanti datanya diganti sumber live (mis. dari data warehouse HR), cukup ganti isi
`load_data()` di `app.py`; seluruh fungsi & chart di bawahnya sudah membaca dari dict `D`
yang dikembalikan fungsi itu, jadi tidak perlu menyentuh bagian lain.
