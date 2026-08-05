import re
import base64
import requests
from datetime import datetime

# ==========================================
# İSTİFADƏÇİ MƏLUMATLARI VƏ AYARLAR
# ==========================================
YOUR_NAME = "GaGoTV"  # Burada adınızı yazın
GITHUB_USERNAME = "GaGoTV"
REPO_NAME = "sport_selcuk-auto_update.py"
FILE_PATH = "selcuksports.m3u"  # GitHub-da görünəcək fayl adı
GITHUB_TOKEN = "GH_PAT_TOKEN"  # GitHub Actions-da Secret kimi ötürüləcək

# Selçuksports canlı domen ünvanı
BASE_URL = "https://www.selcuksportshd.com"  # Güncəl domeni yazın

def get_channel_stream(channel_slug):
    """Kanal səhifəsindən tokenli axın URL-ini çəkir"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": BASE_URL
    }
    try:
        url = f"{BASE_URL}/izle.php?page={channel_slug}"
        res = requests.get(url, headers=headers, timeout=10)
        
        # iframe və ya m3u8 token URL-ini tapırıq
        match = re.search(r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']', res.text)
        if match:
            return match.group(1)
        
        # Alternativ iframe strukturu üçün
        iframe_match = re.search(r'src=["\']([^"\']*player[^"\']*)["\']', res.text)
        if iframe_match:
            iframe_url = iframe_match.group(1)
            iframe_res = requests.get(iframe_url, headers=headers, timeout=10)
            m3u8_match = re.search(r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']', iframe_res.text)
            if m3u8_match:
                return m3u8_match.group(1)
    except Exception as e:
        print(f"Xəta ({channel_slug}): {e}")
    return None

def generate_m3u():
    """M3U siyahısını adınızla və avtomatik kanallarla hazırlayır"""
    channels = [
        {"name": "BeIN Sports 1", "slug": "bein-sports-1"},
        {"name": "BeIN Sports 2", "slug": "bein-sports-2"},
        {"name": "BeIN Sports 3", "slug": "bein-sports-3"},
        {"name": "Exxen Spor 1", "slug": "exxen-1"},
        {"name": "S Sport 1", "slug": "ssport-1"},
        {"name": "Smart Spor", "slug": "smart-spor"}
    ]

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Header hissəsində müəlliflik hüququ sizin adınıza qeyd olunur
    m3u_content = f"#EXTM3U x-tvg-url=\"\"\n"
    m3u_content += f"# ===== CREATED BY {YOUR_NAME} =====\n"
    m3u_content += f"# Last Auto-Update: {now}\n"
    m3u_content += f"# Status: Active Tokens\n\n"

    for ch in channels:
        stream_url = get_channel_stream(ch["slug"])
        if stream_url:
            m3u_content += f'#EXTINF:-1 group-title="Spor" tvg-logo="", {ch["name"]}\n'
            m3u_content += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0\n'
            m3u_content += f'#EXTVLCOPT:http-referrer={BASE_URL}\n'
            m3u_content += f'{stream_url}\n\n'
    
    return m3u_content

def update_github(content):
    """Yenilənmiş faylı GitHub Repositoriyasına push edir"""
    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Əgər fayl artıq varsa, sha ID-sini alırıq
    get_file = requests.get(api_url, headers=headers)
    sha = get_file.json().get("sha") if get_file.status_code == 200 else None

    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": f"Auto update tokens - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        "content": encoded_content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    res = requests.put(api_url, json=payload, headers=headers)
    if res.status_code in [200, 201]:
        print("GitHub faylı uğurla yeniləndi!")
    else:
        print("GitHub Update Xətası:", res.json())

if __name__ == "__main__":
    playlist = generate_m3u()
    update_github(playlist)
