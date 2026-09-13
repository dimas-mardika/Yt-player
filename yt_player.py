import os
import subprocess
import sys
from yt_dlp import YoutubeDL

def cari_lagu_youtube(query, limit=5):
    """Mencari daftar lagu di YouTube berdasarkan kata kunci."""
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
            print(f"❌ Gagal mengambil data dari YouTube: {e}")
            return []

def get_direct_audio_url(video_url):
    """Mendapatkan link direct stream audio dari YouTube."""
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
            print(f"❌ Error ekstraksi audio stream: {e}")
            return None

def putar_audio(video_url, judul):
    """Memutar direct stream audio pakai mpv."""
    print(f"\n⏳ Memproses audio untuk: {judul}...")
    direct_url = get_direct_audio_url(video_url)
    
    if not direct_url:
        print("❌ Gagal memutar lagu ini. Coba lagu lain.")
        input("\nTekan Enter untuk kembali...")
        return

    print(f"\n▶️ Memutar: {judul}")
    print("--------------------------------------------------")
    print("💡 KONTROL KEYBOARD MPV:")
    print("   [SPASI] = Pause / Play")
    print("   [ 9 ] / [ 0 ] = Kecilkan / Besarkan Volume")
    print("   [ q ] = Stop & Kembali ke Menu (Ganti Lagu)")
    print("--------------------------------------------------\n")
    
    mpv_cmd = "mpv"
    if os.path.exists(".\\mpv.exe"):
        mpv_cmd = ".\\mpv.exe"
        
    cmd = [
        mpv_cmd,
        "--no-video",
        "--volume=100",
        "--input-terminal=yes",
        "--term-osd-bar",
        direct_url  # Umpankan URL audio langsung, bukan link YouTube!
    ]
    
    try:
        process = subprocess.Popen(cmd)
        process.wait()
    except Exception as e:
        print(f"❌ Error memutar audio: {e}")
    except KeyboardInterrupt:
        print("\n⏹️ Musik dihentikan.")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==================================================")
        print("       🎵 PYTHON YOUTUBE TERMINAL PLAYER 🎵       ")
        print("==================================================")
        
        keyword = input("\nKetik nama artis / judul lagu (atau 'q' buat keluar): ").strip()
        
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