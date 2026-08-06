import json
import urllib.request
import urllib.parse
import sys

SERVERS = ["https://vavoo.to/live2/index", "https://vavoo.to/live/index"]
AUTH_URL = "https://vavoo.to/app/v3/session/ping"

headers = {
    "User-Agent": "VAVOO/2.6",
    "Accept": "*/*",
    "Content-Type": "application/json"
}

def get_auth_token():
    # Vavoo sessiyası yaradıb aktual token almaq
    body_data = json.dumps({"token": "", "box_id": "12345"}).encode('utf-8')
    try:
        req = urllib.request.Request(AUTH_URL, data=body_data, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            token = data.get("token") or data.get("signature")
            if token:
                return token
    except Exception as e:
        print(f"Session ping xətası: {e}")

    # Ehtiyat variant (Signature API)
    try:
        sig_req = urllib.request.Request("https://vavoo.to/app/v3/signature", headers={"User-Agent": "VAVOO/2.6"})
        with urllib.request.urlopen(sig_req, timeout=10) as sig_res:
            data = json.loads(sig_res.read().decode())
            return data.get("signature")
    except Exception as e:
        print(f"Signature xətası: {e}")

    return None

def fetch_channels(token):
    channels = []
    url_suffix = f"?token={token}" if token else ""
    
    for server in SERVERS:
        try:
            req = urllib.request.Request(f"{server}{url_suffix}", headers={"User-Agent": "VAVOO/2.6"})
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                if isinstance(data, list):
                    channels.extend(data)
                    break
        except Exception as e:
            print(f"Server xətası ({server}): {e}")
            continue

    return channels

def generate_m3u():
    token = get_auth_token()
    print(f"Alınan Token: {token}")

    if not token:
        print("CRITICAL: Token alına bilmədi! İş dayandırılır.")
        sys.exit(1) # Token olmasa faylı yanlış yazmasın

    channels = fetch_channels(token)
    if not channels:
        print("Kanal tapılmadı.")
        return

    m3u_content = "#EXTM3U\n"
    tr_count = 0

    for ch in channels:
        country = str(ch.get("group", "")) or str(ch.get("country", ""))
        
        # Yalnız Türk kanallarını filtrləyirik
        if "Turkey" in country or "TR" in country or ch.get("language") == "tr":
            name = ch.get("name", "Bilinməyən Kanal")
            url = ch.get("url", "")
            logo = ch.get("logo", "")
            
            if url:
                # Token-in düzgün birləşdirilməsi
                clean_url = url.split("?")[0]
                stream_url = f"{clean_url}?token={token}"
                
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="Turk", {name}\n'
                m3u_content += f'#EXTVLCOPT:http-user-agent=VAVOO/2.6\n'
                m3u_content += f"{stream_url}|User-Agent=VAVOO/2.6\n"
                tr_count += 1

    with open("vavoo_tr.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Uğurlu! Cəmi {tr_count} Türk kanalı 'vavoo_tr.m3u' faylına yazıldı.")

if __name__ == "__main__":
    generate_m3u()
