# Proyek Analisis Data: Bike Sharing Dataset

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011-2012) beserta dashboard interaktif menggunakan Streamlit.

## Pertanyaan Bisnis
1. Pada jam berapa puncak penyewaan terjadi pada hari kerja dibandingkan akhir pekan/libur?
2. Berapa persen penurunan penyewaan harian saat cuaca berkabut dan hujan/salju ringan dibanding cuaca cerah, dan pada rentang suhu berapa penyewaan tertinggi?
3. Berapa pertumbuhan penyewaan 2012 vs 2011, bulan apa yang tertinggi/terendah, dan bagaimana komposisi pengguna registered vs casual?

## Struktur Direktori
```
submission
├───dashboard
| ├───main_data.csv      (data per jam yang sudah dibersihkan)
| ├───day_clean.csv      (data harian yang sudah dibersihkan)
| └───dashboard.py
├───data
| ├───day.csv
| └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment
Menggunakan terminal/shell (Python 3.9+):
```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Atau menggunakan Anaconda:
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Menjalankan Dashboard
Dari folder `submission`:
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di browser pada `http://localhost:8501`.

## Menjalankan Ulang Notebook
Buka `notebook.ipynb` dari folder `submission` (agar path `data/` dan `dashboard/` terbaca), lalu jalankan semua sel. Sel terakhir akan mengekspor `main_data.csv` dan `day_clean.csv` ke folder `dashboard`.

## Sumber Data
Fanaee-T, Hadi, and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge", Progress in Artificial Intelligence (2013): pp. 1-15, Springer Berlin Heidelberg, doi:10.1007/s13748-013-0040-3.
