import requests
import re

# Kanal səhifələrinin tam siyahısı
CHANNELS = {
    "ARB Günəş": "https://www.canlitv.com/arb-gunes",
    "AZTV": "https://www.canlitv.com/aztv",
    "İctimai TV": "https://www.canlitv.com/itv-canli",
    "Space TV": "https://www.canlitv.com/space-tv-canli-izle",
    "CBC Sport": "https://www.canlitv.com/cbc-sport"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.canlitv.com/"
}

def fetch_m3u8_link(page_url):
    try:
        session = requests.Session()
        # 1. Əsas səhifəni yükləyirik
        res = session.get(page_url, headers=headers, timeout=10)
        
        # Səhifə daxilində birbaşa .m3u8 varmı?
        m3u8_matches = re.findall(r'https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*', res.text)
        if m3u8_matches:
            return m3u8_matches[0]

        # 2. Əgər iframe daxilindədirsə, iframe src tapırıq
        iframe_matches = re.findall(r'<iframe[^\n>]+src=["\']([^"\']+)["\']', res.text)
        for embed_url in iframe_matches:
            if not embed_url.startswith('http'):
                embed_url = "https:" + embed_url if embed_url.startswith('//') else "https://www.canlitv.com" + embed_url
            
            embed_res = session.get(embed_url, headers=headers, timeout=10)
            embed_m3u8 = re.findall(r'https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*', embed_res.text)
            if embed_m3u8:
                return embed_m3u8[0]
                
    except Exception as e:
        print(f"Xəta ({page_url}): {e}")
    return None

def main():
    m3u_content = "#EXTM3U\n\n"
    success_count = 0

    for name, page_url in CHANNELS.items():
        print(f"Axtarılır: {name}...")
        link = fetch_m3u8_link(page_url)
        
        if link:
            # HTML escape simvollarını təmizləyirik
            clean_link = link.replace("&amp;", "&")
            m3u_content += f'#EXTINF:-1 group-title="AZERBAIJAN", {name}\n{clean_link}\n\n'
            print(f"-> {name}: Tapıldı!")
            success_count += 1
        else:
            print(f"-> {name}: Tapılmadı.")

    with open("playlist.m3u8", "w", encoding="utf-8") as f:
        f.write(m3u_content)
        
    print(f"\nYekun: {success_count} kanal əlavə olundu.")

if __name__ == "__main__":
    main()
