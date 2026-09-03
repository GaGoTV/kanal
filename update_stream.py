import requests
import re

# Kanalların id-ləri və ya birbaşa axın keçidləri
CHANNELS = {
    "ARB Günəş": "http://yayin2.canlitv.fun/live/arbgunes.stream/playlist.m3u8",
    "AZTV": "http://yayin2.canlitv.fun/live/aztv.stream/playlist.m3u8",
    "İctimai TV": "http://yayin2.canlitv.fun/live/itv.stream/playlist.m3u8",
    "CBC Sport": "http://yayin2.canlitv.fun/live/cbcsport.stream/playlist.m3u8",
    "Space TV": "http://yayin2.canlitv.fun/live/spacetv.stream/playlist.m3u8"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.canlitv.com/"
}

def get_real_m3u8(stream_url):
    try:
        # Birbaşa stream серверindən dinamik chunklist keçidini alırıq
        res = requests.get(stream_url, headers=headers, timeout=10)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if line.endswith('.m3u8') or 'chunklist' in line:
                    if line.startswith('http'):
                        return line
                    # Nisbi keçiddirsə tam URL yaradırıq
                    base_url = stream_url.rsplit('/', 1)[0]
                    return f"{base_url}/{line}"
            return stream_url
    except Exception as e:
        print(f"Xəta: {e}")
    return None

def main():
    m3u_content = "#EXTM3U\n\n"
    for name, base_stream in CHANNELS.items():
        print(f"Yenilənir: {name}...")
        final_url = get_real_m3u8(base_stream)
        if final_url:
            m3u_content += f'#EXTINF:-1 group-title="AZERBAIJAN", {name}\n{final_url}\n\n'
            print(f"-> {name}: Uğurlu!")
        else:
            print(f"-> {name}: Alınmadı")

    with open("playlist.m3u8", "w", encoding="utf-8") as f:
        f.write(m3u_content)

if __name__ == "__main__":
    main()
