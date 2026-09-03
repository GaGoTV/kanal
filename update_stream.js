const fs = require('fs');
const puppeteer = require('puppeteer');

const CHANNELS = {
    "ARB Günəş": "https://www.canlitv.com/arb-gunes",
    "AZTV": "https://www.canlitv.com/aztv",
    "İctimai TV": "https://www.canlitv.com/itv-canli",
    "Space TV": "https://www.canlitv.com/space-tv-canli-izle",
    "CBC Sport": "https://www.canlitv.com/cbc-sport"
};

async function getStreamUrl(browser, pageUrl) {
    const page = await browser.newPage();
    let streamUrl = null;

    // Şəbəkə sorğularını dinləyirik və .m3u8 keçidini tuturuq
    page.on('request', request => {
        const url = request.url();
        if (url.includes('.m3u8') || url.includes('canlitv.fun/live/')) {
            if (!streamUrl) streamUrl = url;
        }
    });

    try {
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');
        await page.goto(pageUrl, { waitUntil: 'networkidle2', timeout: 30000 });
        await new Promise(r => setTimeout(r, 3000)); // Pleyerin yüklənməsini gözləyirik
    } catch (e) {
        console.log(`Xəta (${pageUrl}):`, e.message);
    } finally {
        await page.close();
    }

    return streamUrl;
}

async function main() {
    const browser = await puppeteer.launch({
        headless: "new",
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    let m3uContent = "#EXTM3U\n\n";

    for (const [name, url] of Object.entries(CHANNELS)) {
        console.log(`Yüklənir: ${name}...`);
        const m3u8Link = await getStreamUrl(browser, url);

        if (m3u8Link) {
            m3uContent += `#EXTINF:-1 group-title="AZERBAIJAN", ${name}\n${m3u8Link}\n\n`;
            console.log(`-> ${name}: Uğurla tapıldı!`);
        } else {
            console.log(`-> ${name}: Keçid tapılmadı.`);
        }
    }

    await browser.close();
    fs.writeFileSync('playlist.m3u8', m3uContent, 'utf-8');
    console.log("playlist.m3u8 faylı yeniləndi!");
}

main();
