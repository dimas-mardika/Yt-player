import os
import subprocess
import shutil
import sys

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("❌ Modul 'yt-dlp' belum terinstall.")
    print("💡 Jalankan perintah: py -m pip install yt-dlp")
    sys.exit(1)

def cari_lagu_youtube(query, limit=5):
    """Mencari daftar lagu di YouTube."""
    print(f"\n🔍 Mencari lagu: '{query}' di YouTube...\n")
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch'
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            results = info.get('entries', [])
            return [r for r in results if r]
        except Exception as e:
            print(f"❌ Error pencarian: {e}")
            return []

def ambil_direct_stream_url(video_url):
    """Mendapatkan URL audio langsung agar MPV tidak perlu ekstraksi ulang."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            return info.get('url')
        except Exception as e:
            print(f"❌ Gagal mengambil stream URL: {e}")
            return None

def cari_mpv_path():
    """Mencari lokasi mpv.exe di sistem PATH atau instalasi winget."""
    mpv_cmd = shutil.which("mpv")
    if mpv_cmd:
        return mpv_cmd
    return "mpv"

def putar_audio(video_url, judul):
    """Memutar audio menggunakan MPV native sistem."""
    print("⏳ Menyiapkan stream audio...")
    stream_url = ambil_direct_stream_url(video_url)
    
    if not stream_url:
        print("❌ Gagal memproses link audio.")
        input("\nTekan Enter untuk melanjutkan...")
        return

    mpv_bin = cari_mpv_path()
    
    print(f"\n▶️ Memutar: {judul}")
    print("--------------------------------------------------")
    print("💡 KONTROL KEYBOARD MPV:")
    print("   [SPASI] = Pause / Play")
    print("   [ 9 ] / [ 0 ] = Kecilkan / Besarkan Volume")
    print("   [ q ] = Stop & Kembali ke Menu (Ganti Lagu)")
    print("--------------------------------------------------\n")

    cmd = [
        mpv_bin,
        "--no-video",
        "--volume=100",
        "--input-terminal=yes",
        "--term-osd-bar",
        "--no-ytdl",
        stream_url
    ]
    
    try:
        process = subprocess.Popen(cmd)
        process.wait()
    except FileNotFoundError:
        print(f"❌ Error: Executable MPV tidak ditemukan.")
        input("\nTekan Enter untuk melanjutkan...")
    except Exception as e:
        print(f"❌ Error memutar audio: {e}")
        input("\nTekan Enter untuk melanjutkan...")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==================================================")
        print("    🎵 PYTHON YOUTUBE LITE PLAYER (< 20 KB) 🎵    ")
        print("==================================================")
        
        keyword = input("\nKetik nama lagu / artis (atau 'q' untuk keluar): ").strip()
        if keyword.lower() == 'q':
            print("Sampai jumpa, bro! 👋")
            break
        if not keyword:
            continue
            
        lagu_list = cari_lagu_youtube(keyword, limit=5)
        if not lagu_list:
            print("Lagu tidak ditemukan. Coba kata kunci lain.")
            input("\nTekan Enter untuk mencoba lagi...")
            continue
            
        print("==================================================")
        print(f" HASIL PENCARIAN UNTUK: '{keyword.upper()}'")
        print("==================================================")
        for i, item in enumerate(lagu_list, start=1):
            judul = item.get('title', 'Unknown Title')
            uploader = item.get('uploader', 'Unknown Channel')
            print(f"[{i}] {judul} ({uploader})")
        print("[0] Batal / Cari Lagi")
        print("--------------------------------------------------")
        
        pilihan = input("Pilih nomor lagu yang mau diputar (1-5): ").strip()
        if pilihan.isdigit():
            idx = int(pilihan) - 1
            if 0 <= idx < len(lagu_list):
                selected = lagu_list[idx]
                video_url = selected.get('webpage_url') or f"https://www.youtube.com/watch?v={selected['id']}"
                judul_lagu = selected.get('title', 'Lagu Selected')
                putar_audio(video_url, judul_lagu)

if __name__ == "__main__":
    main()