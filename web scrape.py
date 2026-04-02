import requests
from bs4 import BeautifulSoup
import pandas as pd
import time # Tambahkan ini di paling atas

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

url = "https://www.detik.com/search/searchall?query=saham+bumi"
response = requests.get(url, headers=headers)

# Kita ubah kode HTML mentah menjadi objek BeautifulSoup agar bisa diaduk-aduk
soup = BeautifulSoup(response.text, 'html.parser')

# Mencari semua kotak berita
articles = soup.find_all('article', class_='list-content__item')

data_berita = [] # Tempat sampah sementara untuk menampung data

# Kita ambil halaman 1 sampai 3 
for page in range(1, 11):
    print(f"Sedang mengambil data dari halaman {page}...")
    
    # Masukkan variabel 'page' ke dalam URL
    url = f"https://www.detik.com/search/searchall?query=saham+bumi&page={page}"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='list-content__item')
    
    for article in articles:
        title_container = article.find('h3', class_='media__title')
        if title_container:
            title_element = title_container.find('a')
            if title_element:
                data_berita.append({
                    'Judul': title_element.get_text(strip=True),
                    'Link': title_element['href'],
                    'Tanggal': article.find('div', class_='media__date').get_text(strip=True) if article.find('div', class_='media__date') else "N/A"
                })
    
    # PENTING: Kasih jeda 2 detik agar server tidak menganggapmu serangan bot
    time.sleep(2)


# Simpan setelah semua halaman selesai diambil
df = pd.DataFrame(data_berita)
df['Tanggal_Clean'] = df['Tanggal'].str.split(',').str[-1].str.replace('WIB', '').str.strip()
df['Tanggal_Clean'] = pd.to_datetime(df['Tanggal_Clean'], errors='coerce')
# Ubah semua judul jadi huruf kecil (lowercase) agar pencarian tidak sensitif huruf besar/kecil
# Lalu cek apakah kata 'bumi' ada di dalam judul tersebut
df_filtered = df[df['Judul'].str.lower().str.contains('bumi')]
# Filter hanya untuk tahun 2026
df_2026 = df[df['Tanggal_Clean'].dt.year == 2026]

# Hitung ulang jumlah berita per tanggal di tahun 2026
tren_berita = df_2026.groupby(df_2026['Tanggal_Clean'].dt.date).size()

# Simpan hasil yang sudah difilter
df_filtered.to_csv('hasil_scraping_bumi_bersih.csv', index=False)

print(f"Total awal: {len(df)}")
print(f"Setelah difilter: {len(df_filtered)}")
df.to_csv('hasil_scraping_detik_banyak.csv', index=False)
print(f"Selesai! Total {len(data_berita)} berita berhasil diambil.")

# --- BAGIAN VISUALISASI ---

# 1. Pastikan kolom ini DIBUAT dulu sebelum dipanggil
# Kita ambil teks tanggal, buang 'WIB', lalu ubah jadi format waktu Python


# 2. Hapus data yang gagal diubah jadi tanggal (supaya tidak error saat difilter)
df = df.dropna(subset=['Tanggal_Clean'])

# 3. BARU SEKARANG kamu bisa filter tahun 2026
df_2026 = df[df['Tanggal_Clean'].dt.year == 2026]

# 4. Buat tren berita
tren_berita = df_2026.groupby(df_2026['Tanggal_Clean'].dt.date).size()

# --- BAGIAN VISUALISASI (PROFESSIONAL VERSION) ---
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # Tambahkan ini untuk mengatur tanggal

# 1. Hitung tren dari df_2026
tren_berita = df_2026.groupby(df_2026['Tanggal_Clean'].dt.date).size()

# 2. Setup Figure & Style
# Gunakan style 'seaborn-v0_8-whitegrid' agar terlihat modern dan bersih
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.figure(figsize=(14, 7)), plt.gca()

# 3. Plot Data (Ubah jadi Grafik Garis yang Tebal)
# Gunakan warna Navy yang elegan, marker 'o' di setiap titik data
tren_berita.plot(kind='line', marker='o', color='#001F5B', 
                 linewidth=3, markersize=8, label='Jumlah Berita')

# 4. MEMPERCANTIK SUMBU X (Tanggal)
# Agar tanggal tidak bertumpuk, kita tampilkan per 2 hari sekali saja
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2)) 
# Format tanggal jadi '30 Mar' (Hari Bulan) agar ringkas
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

# 5. Tambahkan Label, Judul, & Estetika
plt.title('Tren Frekuensi Berita Saham $BUMI (Maret - April 2026)', 
          fontsize=18, fontweight='bold', pad=20, color='#333333')
plt.xlabel('Tanggal', fontsize=14, fontweight='bold')
plt.ylabel('Jumlah Berita', fontsize=14, fontweight='bold')

# Rotasi tanggal agar miring 45 derajat (biar tidak tabrakan)
plt.xticks(rotation=45, ha='right', fontsize=11)
plt.yticks(fontsize=11)

# Tambahkan legenda dan layout yang pas
plt.legend(fontsize=12)
plt.tight_layout()

# 6. Simpan Hasil Akhir
plt.savefig('tren_berita_bumi_pro.png', dpi=300) # dpi=300 agar gambar tajam
print("Grafik profesional berhasil disimpan sebagai 'tren_berita_bumi_pro.png'")
plt.show()