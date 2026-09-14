# ==============================================================================
# 🎵 PYTHON YOUTUBE, RADIO, PLAYLIST & LYRICS LITE PLAYER (< 20 KB)
# Developed & Created by Dimas Mardika
# License: MIT
# Description: Ultra-lightweight terminal player with YT, Radio, Playlist & Lyrics.
# ==============================================================================

import os
import subprocess
import shutil
import sys
import json
import urllib.request
import urllib.parse
import re
import time
import threading

PLAYLIST_FILE = "playlist.json"

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("❌ Waduh, modul 'yt-dlp' belum ke-install nih, bro!")
    print("💡 Coba running command ini dulu ya: py -m pip install yt-dlp")
    sys.exit(1)

# --- FUNGSI MANAJEMEN PLAYLIST (JSON) ---
def muat_playlist():
    if not os.path.exists(PLAYLIST_FILE):
        return []
    try:
        with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def simpan_ke_playlist(judul, video_url):
    playlist = muat_playlist()
    if any(item['url'] == video_url for item in playlist):
        print(f"\n⚠️ Lagu '{judul}' udah ada di playlist kamu, bro!")
    else:
        playlist.append({"judul": judul, "url": video_url})
        with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(playlist, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Berhasil nambahin '{judul}' ke playlist!")
    input("\nTekan Enter buat lanjut...")

def hapus_dari_playlist(index):
    playlist = muat_playlist()
    if 0 <= index < len(playlist):
        removed = playlist.pop(index)
        with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(playlist, f, indent=4, ensure_ascii=False)
        print(f"\n🗑️ Berhasil ngapus '{removed['judul']}' dari playlist.")
    input("\nTekan Enter buat lanjut...")

# --- FUNGSI LYRICS ENGINE (LRCLIB API) ---
def bersihkan_judul_lagu(judul):
    """Membersihkan kata-kata sampah dari judul YouTube agar pencarian API akurat."""
    pattern = r'\(.*?\)|\[.*?\]|official|music|video|audio|lyric|lyrics|hd|mv|remastered|ft\..*|feat\..*'
    clean = re.sub(pattern, '', judul, flags=re.IGNORECASE)
    return clean.strip()

def ambil_data_lirik(judul_lagu):
    """Mengambil lirik dari LRCLIB API. Mengembalikan tuple (synced_lrc, plain_lrc)."""
    judul_clean = bersihkan_judul_lagu(judul_lagu)
    query = urllib.parse.quote(judul_clean)
    url = f"https://lrclib.net/api/search?q={query}"
    
    headers = {'User-Agent': 'PythonTerminalPlayer/1.0'}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            results = json.loads(response.read().decode())
            for item in results:
                synced = item.get("syncedLyrics")
                plain = item.get("plainLyrics")
                if synced or plain:
                    return synced, plain
    except Exception:
        pass
    return None, None

def parse_lrc(lrc_text):
    """Mengurai teks LRC format [mm:ss.xx] menjadi list tuple (detik, teks_lirik)."""
    lirik_list = []
    pattern = re.compile(r'\[(\d{2}):(\d{2}\.\d{2})\](.*)')
    for line in lrc_text.splitlines():
        match = pattern.match(line)
        if match:
            menit = int(match.group(1))
            detik = float(match.group(2))
            total_detik = menit * 60 + detik
            teks = match.group(3).strip()
            if teks:
                lirik_list.append((total_detik, teks))
    return sorted(lirik_list, key=lambda x: x[0])

def jalankan_auto_lirik(synced_lrc, stop_event):
    """Menjalankan animasi lirik auto-scroll di thread terpisah."""
    lirik_parsed = parse_lrc(synced_lrc)
    if not lirik_parsed:
        return

    waktu_mulai = time.time()
    for timestamp, teks in lirik_parsed:
        if stop_event.is_set():
            break
        waktu_sekarang = time.time() - waktu_mulai
        tunggu = timestamp - waktu_sekarang
        if tunggu > 0:
            time.sleep(tunggu)
        if stop_event.is_set():
            break
        print(f"🎤 {teks}")

# --- FUNGSI RADIO API ---
def cari_radio_online(query, limit=10):
    print(f"\n📡 Searching stasiun radio: '{query}' di database global...\n")
    encoded_query = urllib.parse.quote(query)
    url = f"https://de1.api.radio-browser.info/json/stations/byname/{encoded_query}?limit={limit}"
    headers = {'User-Agent': 'PythonTerminalRadio/1.0'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Gagal nyambung ke Radio API: {e}")
        return []

# --- CORE PLAYER ENGINE ---
def cari_mpv_path():
    mpv_cmd = shutil.which("mpv")
    return mpv_cmd if mpv_cmd else "mpv"

def ambil_direct_stream_url(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 10,
        'source_address': '0.0.0.0',
        'nocheckcertificate': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            return info.get('url')
        except Exception as e:
            print(f"❌ Amsyong, gagal extract stream link: {e}")
            return None

def putar_audio(stream_url, judul, is_youtube=True):
    mpv_bin = cari_mpv_path()
    
    synced_lrc, plain_lrc = None, None
    stop_lirik_event = threading.Event()
    lirik_thread = None

    if is_youtube:
        print("\n⏳ Checking lirik lagu...")
        synced_lrc, plain_lrc = ambil_data_lirik(judul)

    # 1. CLEAR SCREEN DULU
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 2. TAMPILKAN HEADER DASHBOARD & KONTROL
    print("==================================================")
    print("            🎧 NOW PLAYING DASHBOARD 🎧            ")
    print("==================================================")
    print(f"🎵 Judul : {judul}")
    print("--------------------------------------------------")
    print("💡 KONTROL KEYBOARD DIRECT MPV:")
    print("   [ SPASI ] = Pause / Play")
    print("   [  9  ]   = Kecilkan Volume")
    print("   [  0  ]   = Besarkan Volume")
    print("   [  q  ]   = Stop & Kembali ke Menu")
    print("--------------------------------------------------")

    # 3. TAMPILKAN LIRIK SECARA UTUH KESELURUHAN (BIAR GAK HILANG/TERTIMPA MPV)
    if is_youtube:
        if plain_lrc or synced_lrc:
            print("📜 TEKS LIRIK LAGU:")
            print("--------------------------------------------------")
            # Jika ada plain_lrc gunakan itu, jika tidak ada ekstrak dari synced_lrc
            if plain_lrc:
                print(plain_lrc)
            elif synced_lrc:
                parsed = parse_lrc(synced_lrc)
                for _, teks in parsed:
                    print(f"🎤 {teks}")
            print("--------------------------------------------------")
        else:
            print("ℹ️ Status Lirik: Tidak ditemukan di database.\n")

    print("\n📊 LIVE PLAYER STREAM & PROGRESS BAR:")
    print()

    cmd = [
        mpv_bin,
        "--no-video",
        "--volume=100",
        "--input-terminal=yes",
        "--term-osd-bar",
        "--network-timeout=10"
    ]
    if is_youtube:
        cmd.append("--no-ytdl")
    cmd.append(stream_url)
    
    try:
        process = subprocess.Popen(cmd)
        process.wait()
    except KeyboardInterrupt:
        process.kill()
        print("\n\n⏹️ Playback stopped. Kembali ke menu...")
        
def cari_lagu_youtube(query, limit=5):
    print(f"\n🔍 OTW nyari lagu: '{query}' di YouTube...\n")
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'socket_timeout': 10,
        'source_address': '0.0.0.0',
        'nocheckcertificate': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            results = info.get('entries', [])
            return [r for r in results if r]
        except Exception as e:
            print(f"❌ Error pas nyari: {e}")
            return []

# --- SUB MENUS ---
def menu_youtube():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==================================================")
        print("            🔍 YOUTUBE MUSIC SEARCH 🎵            ")
        print("==================================================")
        keyword = input("\nKetik judul lagu / artist (atau 'q' buat back): ").strip()
        if keyword.lower() == 'q' or not keyword:
            break
            
        lagu_list = cari_lagu_youtube(keyword, limit=5)
        if not lagu_list:
            print("Zonk! Lagunya gak ketemu. Coba kata kunci lain.")
            input("\nTekan Enter buat nyoba lagi...")
            continue
            
        print("==================================================")
        print(f" HASIL SEARCHING BUAT: '{keyword.upper()}'")
        print("==================================================")
        for i, item in enumerate(lagu_list, start=1):
            judul = item.get('title', 'Unknown Title')
            uploader = item.get('uploader', 'Unknown Channel')
            print(f"[{i}] {judul} ({uploader})")
        print("[0] Cancel / Search Ulang")
        print("--------------------------------------------------")
        
        pilihan = input("Pilih nomor lagu (1-5): ").strip()
        if pilihan.isdigit():
            idx = int(pilihan) - 1
            if 0 <= idx < len(lagu_list):
                selected = lagu_list[idx]
                video_url = selected.get('webpage_url') or f"https://www.youtube.com/watch?v={selected['id']}"
                judul_lagu = selected.get('title', 'Lagu Selected')
                
                print("\n[1] Directly Play Now")
                print("[2] Save to My Playlist ❤️")
                aksi = input("Pilih opsi (1/2): ").strip()
                
                if aksi == '2':
                    simpan_ke_playlist(judul_lagu, video_url)
                else:
                    print("⏳ Wait ya, lagi nyiapin stream audio-nya...")
                    stream_url = ambil_direct_stream_url(video_url)
                    if stream_url:
                        putar_audio(stream_url, judul_lagu, is_youtube=True)

def menu_radio():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==================================================")
        print("     📻 GLOBAL RADIO SEARCH & PLAYER (API) 📻     ")
        print("==================================================")
        keyword = input("\nKetik nama radio / kota / genre (atau 'q' buat back): ").strip()
        if keyword.lower() == 'q' or not keyword:
            break
            
        radio_list = cari_radio_online(keyword, limit=10)
        if not radio_list:
            print("Zonk! Stasiun radio gak ketemu.")
            input("\nTekan Enter buat nyoba lagi...")
            continue
            
        print("==================================================")
        print(f" HASIL SEARCHING RADIO BUAT: '{keyword.upper()}'")
        print("==================================================")
        for i, station in enumerate(radio_list, start=1):
            nama = station.get('name', 'Unknown Radio').strip()
            negara = station.get('countrycode', 'INTL')
            tags = station.get('tags', 'music')[:30]
            print(f"[{i}] {nama} [{negara}] - ({tags})")
        print("[0] Cancel / Search Ulang")
        print("--------------------------------------------------")
        
        pilihan = input(f"Pilih nomor radio (1-{len(radio_list)}) atau 0 Batal: ").strip()
        if pilihan.isdigit():
            idx = int(pilihan) - 1
            if 0 <= idx < len(radio_list):
                selected = radio_list[idx]
                stream_url = selected.get('url_resolved') or selected.get('url')
                nama_radio = selected.get('name', 'Radio Station')
                if stream_url:
                    putar_audio(stream_url, nama_radio, is_youtube=False)

def menu_playlist():
    while True:
        playlist = muat_playlist()
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==================================================")
        print("           ❤️ MY FAVORITE PLAYLIST ❤️            ")
        print("==================================================")
        if not playlist:
            print("Playlist kamu masih kosong nih, bro!")
            print("--------------------------------------------------")
            input("\nTekan Enter buat kembali...")
            break
            
        for i, item in enumerate(playlist, start=1):
            print(f"[{i}] {item['judul']}")
        print("--------------------------------------------------")
        print("[A] Play ALL Songs (Sekaligus)")
        print("[D] Hapus Lagu dari Playlist")
        print("[0] Kembali ke Menu Utama")
        print("--------------------------------------------------")
        
        pilihan = input("Pilih opsi / nomor lagu: ").strip().lower()
        if pilihan == '0':
            break
        elif pilihan == 'a':
            for item in playlist:
                print(f"\n⏳ Extracting: {item['judul']}...")
                stream_url = ambil_direct_stream_url(item['url'])
                if stream_url:
                    putar_audio(stream_url, item['judul'], is_youtube=True)
        elif pilihan == 'd':
            idx = input("Ketik nomor lagu yang mau dihapus: ").strip()
            if idx.isdigit():
                hapus_dari_playlist(int(idx) - 1)
        elif pilihan.isdigit():
            idx = int(pilihan) - 1
            if 0 <= idx < len(playlist):
                selected = playlist[idx]
                print(f"\n⏳ Extracting: {selected['judul']}...")
                stream_url = ambil_direct_stream_url(selected['url'])
                if stream_url:
                    putar_audio(stream_url, selected['judul'], is_youtube=True)

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==================================================")
        print("   🎵 PYTHON YOUTUBE & RADIO LITE (< 20 KB) 🎵    ")
        print("        Developed & Created by Dimas Mardika      ")
        print("==================================================")
        print("[1] 🔍 Search & Play YouTube Tracks")
        print("[2] 📻 Search & Play Global Online Radio")
        print("[3] ❤️ My Favorite Playlist")
        print("[q] 🚪 Exit Application")
        print("--------------------------------------------------")
        
        menu = input("Pilih menu (1/2/3/q): ").strip().lower()
        if menu == 'q':
            print("\nCabut dulu, bro! Catch you later 👋🔥\n")
            break
        elif menu == '1':
            menu_youtube()
        elif menu == '2':
            menu_radio()
        elif menu == '3':
            menu_playlist()

if __name__ == "__main__":
    main()