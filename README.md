# YouTube, Radio & Playlist Lite Player

Pemutar audio berbasis terminal menggunakan Python, `yt-dlp`, dan MPV. Aplikasi
ini bisa mencari lagu di YouTube, memutar radio online, menyimpan playlist
lokal, dan menampilkan lirik jika tersedia.

## Persyaratan

- Windows dengan Python 3 terpasang
- MPV terpasang dan tersedia di `PATH`
- Koneksi internet
- Akses internet ke YouTube, Radio Browser API, dan LRCLIB (untuk lirik)

## Instalasi

1. Install dependensi Python:

   ```powershell
   py -m pip install yt-dlp
   ```

2. Install MPV melalui [situs resmi MPV](https://mpv.io/installation/) atau Windows Package Manager:

   ```powershell
   winget install mpv
   ```

3. Pastikan MPV dapat ditemukan dari terminal:

   ```powershell
   mpv --version
   ```

## Menjalankan

Jalankan aplikasi dari folder project:

```powershell
py yt_player.py
```

Menu yang tersedia:

1. **YouTube**: cari lagu atau artis, pilih salah satu dari lima hasil, lalu
   putar langsung atau simpan ke playlist.
2. **Radio online**: cari stasiun berdasarkan nama, kota, atau genre dari
   Radio Browser.
3. **Playlist**: putar lagu tersimpan satu per satu atau sekaligus, dan hapus
   lagu yang tidak diperlukan.

Saat lagu YouTube diputar, aplikasi mencoba mengambil lirik dari LRCLIB.
Ketersediaan lirik bergantung pada database layanan tersebut.

Playlist disimpan otomatis di file lokal `playlist.json`. File ini sengaja
diabaikan Git karena berisi daftar pribadi pengguna.

## Kontrol MPV

| Tombol | Fungsi |
| --- | --- |
| `Space` | Pause atau play |
| `9` | Mengurangi volume |
| `0` | Menambah volume |
| `q` | Menghentikan lagu dan kembali ke menu |

Kontrol tambahan seperti progress bar ditampilkan langsung oleh MPV saat audio
sedang berjalan.

## Troubleshooting

- **Modul `yt-dlp` belum terinstall**: jalankan `py -m pip install yt-dlp`.
- **MPV tidak ditemukan**: pastikan MPV sudah terinstall dan `mpv --version` berjalan di terminal baru.
- **Pencarian gagal**: periksa koneksi internet atau coba kata kunci lain.
- **Lirik tidak ditemukan**: judul lagu mungkin belum tersedia di LRCLIB; audio
   tetap bisa diputar tanpa lirik.
- **Playlist hilang atau kosong**: pastikan aplikasi dijalankan dari folder
   project agar `playlist.json` yang benar dapat ditemukan.

Gunakan aplikasi ini sesuai aturan dan ketentuan layanan YouTube serta hukum yang berlaku.