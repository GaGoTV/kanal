import re
import requests

# Yeniləmək istədiyiniz bütün kanalların siyahısı
CHANNELS = {
    "ARB Günəş": "https://canlitv.com/arb-gunes-tv?ulke=az",
    "AZTV": "https://www.canlitv.com/aztv",
    "İctimai TV": "https://www.canlitv.com/itv-canli",
    "Space TV": "https://www.canlitv.com/space-tv-canli-izle",
    "CBC Sport": "https://www.canlitv.com/cbc-sport"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_live_url(page_url):
    try:
        response = requests.get(page_url, headers=headers, timeout=10)
        # Səhifənin daxilindən .m3u8 linkini regex ilə tapırıq
        match = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', response.text)
        if match:
            return match.group(0)
    except Exception as e:
        print(f"Xəta ({page_url}): {e}")
    return None

def build_playlist():
    m3u_content = "#EXTM3U\n\n"
    
    for name, url in CHANNELS.items():
        print(f"Yenilənir: {name}...")
        stream_url = get_live_url(url)
        
        if stream_url:
            m3u_content += f"#EXTINF:-1 group-title=\"AZERBAIJAN\", {name}\n{stream_url}\n\n"
        else:
            print(f"--> {name} üçün keçid tapılmadı.")

    with open("playlist.m3u8", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print("Pleylist uğurla yeniləndi və playlist.m3u8 faylına yazıldı!")

if __name__ == "__main__":
    build_playlist()
