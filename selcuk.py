import requests
import re
import os

def find_working_selcuksportshd():
    print("🧭 selcuksportshd domaini kontrol ediliyor...")
    headers = {"User-Agent": "Mozilla/5.0"}

    # Burada sadece sabit bir domain kontrol ediliyor
    url = "https://www.selcuksportshd0f9c045ffb.xyz/"
    print(f"🔍 Kontrol ediliyor: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200 and "uxsyplayer" in response.text:
            print(f"✅ Aktif domain bulundu: {url}")
            return response.text, url
    except Exception as e:
        print(f"⚠️ Hata: {url} ({e})")

    print("❌ Aktif domain bulunamadı.")
    return None, None

def find_dynamic_player_domain(page_html):
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', page_html)
    if match:
        return f"https://{match.group(1)}"
    return None

def extract_base_stream_url(html):
    match = re.search(r'this\.baseStreamUrl\s*=\s*[\'"]([^\'"]+)', html)
    if match:
        return match.group(1)
    return None

def build_m3u8_links(base_stream_url, channel_ids):
    m3u8_links = []
    for cid in channel_ids:
        full_url = f"{base_stream_url}{cid}/playlist.m3u8"
        print(f"✅ M3U8 link oluşturuldu: {full_url}")
        m3u8_links.append((cid, full_url))
    return m3u8_links

def write_m3u_file(m3u8_links, filename="selcuk.m3u", referer=""):
    new_lines = ["#EXTM3U"]

    for cid, url in m3u8_links:
        kanal_adi = cid.replace("-", " ").title()
        new_lines.append(f'#EXTINF:-1, {kanal_adi}')
        new_lines.append(f"#EXTVLCOPT:http-referrer= {referer}")
        new_lines.append(url)

    # Dosya her zaman üzerine yazılır, yoksa yeni oluşturulur
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"✅ Güncelleme tamamlandı: {filename}")

# tvg-id ile eşleşecek kanal ID'leri
channel_ids = [
    "selcukksbein1",
    "selcukksbein2",
    "selcukksbein3",
    "selcukksbein4",
    "selcukksbein5",
    "selcukksbeinsportsmax1",
    "selcukksbeinsportsmax2",
    "selcukksssport1",
    "selcukksssport2",
    "selcukkssmartspor",
    "selcukkssmartspor2",
    "selcukkstivibuspor1",
    "selcukkstivibuspor2",
    "selcukkstivibuspor3",
    "selcukkstivibuspor4",
    "selcukksbeinsportshaber",
    "selcukksaspor",
    "selcukkseurosport1",
    "selcukkseurosport2",
    "selcukksf1",
    "selcukkstabiispor",
    "selcukkstrt1",
    "selcukkstv8",
    "selcukkstrtspor",
    "selcukkstrtspor2",
    "selcukksatv",
    "selcukksdazn1",
    "selcukksdazn2"
]

# Ana işlem
html, referer_url = find_working_selcuksportshd()

if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        print(f"\n🔗 Yayın domaini bulundu: {stream_domain}")
        try:
            player_page = requests.get(
                f"{stream_domain}/index.php?id={channel_ids[0]}",
                headers={"User-Agent": "Mozilla/5.0", "Referer": referer_url}
            )
            base_stream_url = extract_base_stream_url(player_page.text)
            if base_stream_url:
                print(f"📡 Base stream URL bulundu: {base_stream_url}")
                m3u8_list = build_m3u8_links(base_stream_url, channel_ids)
                write_m3u_file(m3u8_list, referer=referer_url)
            else:
                print("❌ baseStreamUrl bulunamadı.")
        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")
    else:
        print("❌ Yayın domaini bulunamadı.")
else:
    print("⛔ Aktif yayın alınamadı.")
