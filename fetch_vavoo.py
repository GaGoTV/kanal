import json
import time
import urllib.request
import sys

# Vavoo Signature və Kanal API ünvanları
SIG_URL = "https://vavoo.to/app/v3/signature"
CHANNELS_URL = "https://vavoo.to/live2/index"

headers = {
    "User-Agent": "VAVOO/2.6",
    "Accept": "*/*"
}

def get_valid_token():
    # 1-ci cəhd: Signature API
    try:
        req = urllib.request.Request(SIG_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode())
            if isinstance(data, dict) and data.get("signature"):
                return data.get("signature")
            elif isinstance(data, str):
                return data
    except Exception as e:
        print(f"Sig API xətası: {e}")

    # 2-ci cəhd: Ping endpoint
    try:
        ping_url = "https://vavoo.to/app/v3/session/ping"
        payload = json.dumps({"token": "", "box_id": "12345"}).encode('utf-8')
        p_headers = {**headers, "Content-Type": "application/json"}
        req = urllib.request.Request(ping_url, data=payload, headers=p_headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode())
            return data.get("token") or data.get("signature")
    except Exception as e:
        print(f"Ping API xətası: {e}")

    return None

def main():
    token = get_valid_token()
    print(f"Alınan Token: {token}")

    if not token:
        print("XƏTA: Token alına bilmədi. Vavoo sorğuna cavab vermədi.")
        sys.exit(1)

    # Kanalları çəkirik
    req_url = f"{CHANNELS_URL}?token={token}"
    try:
        req = urllib.request.Request(req_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as res:
            channels = json.loads(res.read().decode())
    except Exception as e:
        print(f"Kanallar çəkilərkən xəta: {e}")
        sys.exit(1)

    m3u_content = "#EXTM3U\n"
    tr_count = 0

    for ch in channels:
        country = str(ch.get("group", "")) or str(ch.get("country", ""))
        
        # Yalnız Türk kanalları filtri
        if "Turkey" in country or "TR" in country or ch.get("language") == "tr":
            name = ch.get("name", "Bilinməyən Kanal")
            url = ch.get("url", "")
            logo = ch.get("logo", "")
            
            if url:
                clean_url = url.split("?")[0]
                stream_url = f"{clean_url}?token={token}"
                
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" group-title="Turk", {name}\n'
                m3u_content += f'#EXTVLCOPT:http-user-agent=VAVOO/2.6\n'
                m3u_content += f"{stream_url}|User-Agent=VAVOO/2.6\n"
                tr_count += 1

    with open("vavoo_tr.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Uğurlu! {tr_count} Türk kanalı yazıldı.")

if __name__ == "__main__":
    main()
