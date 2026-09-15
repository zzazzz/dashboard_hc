"""
Konversi workbook Excel kasus menjadi file Parquet.

Alasannya: membaca .xlsx berarti membongkar ZIP + parsing XML per sel. Sheet
'Data Kompensasi' (34.916 baris) sendiri makan ~2,8 detik. Parquet menyimpan
data per kolom dalam bentuk biner dengan tipe data yang sudah pasti, jadi
tinggal dibaca langsung ke memori.

Jalankan sekali setiap kali data mentahnya diperbarui:
    python build_cache.py
"""

import time
from pathlib import Path

import pandas as pd

SRC = Path("data/hc_data.xlsx")
OUT = Path("data/parquet")

SHEETS = [
    "Log Pembersihan", "Data Cabang", "Data Karyawan", "Reason Out",
    "Performance Data", "Data Kompensasi", "Performance Cabang", "Engagement Survey",
]


def slug(name: str) -> str:
    return name.lower().replace(" ", "_")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    xls = pd.ExcelFile(SRC)

    t_total = time.time()
    for sheet in SHEETS:
        t = time.time()
        df = xls.parse(sheet)
        # object-dtype kolom teks -> category kalau kardinalitasnya rendah,
        # supaya file lebih kecil dan filter lebih cepat
        text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
        for col in text_cols:
            if df[col].nunique(dropna=False) / max(len(df), 1) < 0.5:
                df[col] = df[col].astype("category")
        path = OUT / f"{slug(sheet)}.parquet"
        df.to_parquet(path, index=False, compression="snappy")
        size_kb = path.stat().st_size / 1024
        print(f"  {sheet:22s} {df.shape!s:14s} -> {path.name:28s} {size_kb:7.1f} KB  ({time.time()-t:.2f}s)")

    print(f"\nSelesai dalam {time.time()-t_total:.2f}s. Output: {OUT}/")


if __name__ == "__main__":
    main()
