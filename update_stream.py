import re
import cloudscraper

# Yenilənəcək kanalların siyahısı
CHANNELS = {
    "ARB Günəş": "https://www.canlitv.com/arb-gunes",
    "AZTV": "https://www.canlitv.com/aztv",
    "İctimai TV": "https://www.canlitv.com/itv-canli",
    "Space TV": "https://www.canlitv.com/space-tv-canli-izle",
    "CBC Sport": "https://www.canlitv.com/cbc-sport"
}

# Cloudflare qorumasını keçmək üçün brauzer imzası
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

def get_live_url(page_url):
    try:
        response = scraper.get(page_url, timeout=15)
        if response.status_code == 200:
            # m3u8 və canlitv.fun keçidlərini tapır
            matches = re.findall(r'https?://[^\s"\'<>]+(?:\.m3u8|canlitv\.fun/live/)[^\s"\'<>]*', response.text)
            if matches:
                clean_url = matches[0].replace('\\/', '/')
                return clean_url
    except Exception as e:
        print(f"Xəta baş verdi ({page_url}): {e}")
    return None

def build_playlist():
    m3u_content = "#EXTM3U\n\n"
    found_count = 0
    
    for name, url in CHANNELS.items():
        print(f"Axtarılır: {name}...")
        stream_url = get_live_url(url)
        
        if stream_url:
            m3u_content += f'#EXTINF:-1 group-title="AZERBAIJAN", {name}\n{stream_url}\n\n'
            found_count += 1
            print(f"-> {name}: Uğurla tapıldı!")
        else:
            print(f"-> {name}: Keçid tapılmadı.")

    with open("playlist.m3u8", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"\nYekun: {found_count} kanal playlist.m3u8 faylına yazıldı.")

if __name__ == "__main__":
    build_playlist()
