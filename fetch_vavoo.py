import json
import urllib.request

# Vavoo API ünvanları
SERVERS = ["https://vavoo.to/live2/index", "https://vavoo.to/live/index"]
SIGNATURE_URL = "https://vavoo.to/app/v3/signature"

headers = {
    "User-Agent": "VAVOO/2.6",
    "Accept": "*/*"
}

def get_auth_token():
    try:
        req = urllib.request.Request(SIGNATURE_URL, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("signature")
    except Exception as e:
        print(f"Token alınarkən xəta: {e}")
        return None

def fetch_channels():
    token = get_auth_token()
    channels = []
    
    for server in SERVERS:
        try:
            req = urllib.request.Request(f"{server}?token={token}", headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if isinstance(data, list):
                    channels.extend(data)
                    break
        except Exception as e:
            print(f"Server xətası ({server}): {e}")
            continue

    return channels

def generate_m3u():
    channels = fetch_channels()
    if not channels:
        print("Kanal tapılmadı.")
        return

    m3u_content = "#EXTM3U\n"
    tr_count = 0

    for ch in channels:
        # Yalnız Türk kanallarını filtrləyirik
        country = ch.get("group", "") or ch.get("country", "")
        if "Turkey" in country or "TR" in country or ch.get("language") == "tr":
            name = ch.get("name", "Bilinməyən Kanal")
            url = ch.get("url", "")
            logo = ch.get("logo", "")
            
            if url:
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="Turk", {name}\n'
                m3u_content += f"{url}\n"
                tr_count += 1

    with open("vavoo_tr.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Uğurlu! Cəmi {tr_count} Türk kanalı 'vavoo_tr.m3u' faylına yazıldı.")

if __name__ == "__main__":
    generate_m3u()
