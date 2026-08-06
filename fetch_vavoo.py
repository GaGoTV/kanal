import json
import uuid
import urllib.request
import urllib.parse

# Vavoo API ünvanları
SERVERS = ["https://vavoo.to/live2/index", "https://vavoo.to/live/index"]
PING_URL = "https://vavoo.to/app/v3/session/ping"

# Təhlükəsizlik üçün keçərli Cihaz ID-si və Headers
device_id = str(uuid.uuid4())

headers = {
    "User-Agent": "VAVOO/2.6",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "x-device-id": device_id
}

def get_auth_token():
    try:
        # Vavoo v3 sessiya pingi generasiya edirik
        payload = json.dumps({"token": "", "device_id": device_id}).encode('utf-8')
        req = urllib.request.Request(PING_URL, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("token") or data.get("signature")
    except Exception as e:
        print(f"Token alına bilmədi, fallback istifadə olunur: {e}")
        # İkinci üsul (Signature fallback)
        try:
            sig_req = urllib.request.Request("https://vavoo.to/app/v3/signature", headers={"User-Agent": "VAVOO/2.6"})
            with urllib.request.urlopen(sig_req, timeout=10) as sig_res:
                return json.loads(sig_res.read().decode()).get("signature")
        except Exception as sig_err:
            print(f"Fallback da xəta verdi: {sig_err}")
            return None

def fetch_channels():
    token = get_auth_token()
    channels = []
    
    for server in SERVERS:
        try:
            url = f"{server}?token={token}" if token else server
            req = urllib.request.Request(url, headers={"User-Agent": "VAVOO/2.6"})
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                if isinstance(data, list):
                    channels.extend(data)
                    break
        except Exception as e:
            print(f"Server xətası ({server}): {e}")
            continue

    return channels, token

def generate_m3u():
    channels, token = fetch_channels()
    if not channels:
        print("Kanal tapılmadı.")
        return

    m3u_content = "#EXTM3U\n"
    tr_count = 0

    for ch in channels:
        country = ch.get("group", "") or ch.get("country", "")
        
        # Yalnız Türk kanalları filtri
        if "Turkey" in country or "TR" in country or ch.get("language") == "tr":
            name = ch.get("name", "Bilinməyən Kanal")
            id_val = ch.get("id", "")
            logo = ch.get("logo", "")
            
            if id_val:
                # Birbaşa m3u8 strim linki
                stream_url = f"https://vavoo.to/live2/index/{id_val}"
                if token:
                    stream_url += f"?token={token}"
                
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="Turk", {name}\n'
                # VLC və OTT Pleyerlər üçün lazımi Headers parametrləri
                m3u_content += f'#EXTVLCOPT:http-user-agent=VAVOO/2.6\n'
                m3u_content += f'#EXTVLCOPT:http-referrer=https://vavoo.to/\n'
                m3u_content += f"{stream_url}|User-Agent=VAVOO/2.6&Referer=https://vavoo.to/\n"
                tr_count += 1

    with open("vavoo_tr.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Uğurlu! Cəmi {tr_count} Türk kanalı 'vavoo_tr.m3u' faylına yazıldı.")

if __name__ == "__main__":
    generate_m3u()
