# YouTube Lite Player

Pemutar audio YouTube berbasis terminal menggunakan Python, `yt-dlp`, dan MPV.

## Persyaratan

- Windows dengan Python 3 terpasang
- MPV terpasang dan tersedia di `PATH`
- Koneksi internet

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

Jalankan dari folder project:

```powershell
py yt_player.py
```

Masukkan nama lagu atau artis, pilih salah satu dari lima hasil pencarian, lalu tekan `q` di MPV untuk kembali ke menu.

## Kontrol MPV

| Tombol | Fungsi |
| --- | --- |
| `Space` | Pause atau play |
| `9` | Mengurangi volume |
| `0` | Menambah volume |
| `q` | Menghentikan lagu dan kembali ke menu |

## Troubleshooting

- **Modul `yt-dlp` belum terinstall**: jalankan `py -m pip install yt-dlp`.
- **MPV tidak ditemukan**: pastikan MPV sudah terinstall dan `mpv --version` berjalan di terminal baru.
- **Pencarian gagal**: periksa koneksi internet atau coba kata kunci lain.

Gunakan aplikasi ini sesuai aturan dan ketentuan layanan YouTube serta hukum yang berlaku.