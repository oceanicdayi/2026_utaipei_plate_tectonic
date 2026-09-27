"""產生「喀拉喀托之子」時事案例的中文教學影片。

每一句旁白 = 一張 1920x1080 投影片（HTML 截圖，內嵌字幕）+ 一段 edge-tts 語音，
最後用 ffmpeg 串成 MP4，並輸出 WebVTT 字幕與封面圖到 ../artifacts/。

用法：python3 video/build_krakatau_video.py
需要：ffmpeg、Noto Sans/Serif CJK TC 字型、playwright（含 Chromium）、edge-tts；合成語音需連網。
修改旁白或畫面：編輯下方 SCENES；只有改過的句子會重新合成語音（以文字內容快取）。
"""
import asyncio
import hashlib
import os
import subprocess
from pathlib import Path

import certifi

# edge-tts 透過 aiohttp 連線且只讀 certifi 的憑證；在需要自訂 CA 的代理環境中改用 SSL_CERT_FILE。
if os.environ.get("SSL_CERT_FILE"):
    certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts"
BUILD = HERE / "build"
VIDEO = ART / "21-krakatau_teaching_video.mp4"
VTT = ART / "21-krakatau_teaching_video.vtt"
POSTER = ART / "21-krakatau_teaching_video_poster.jpg"

VOICE, RATE = "zh-TW-HsiaoChenNeural", "-4%"
LINE_TAIL = 0.3    # 每句之後的停頓（秒）
SCENE_TAIL = 0.9   # 每段最後一句之後再多停的秒數


def img(name):
    return f'<img class="fig" src="{(ART / name).as_uri()}">'


STATS = """
<div class="stats">
  <div class="stat"><b class="t">25</b><span>小時<br>9 月 4–6 日持續噴發</span></div>
  <div class="stat"><b class="t">32.8</b><span>公頃<br>火山本體新增陸地</span></div>
  <div class="stat"><b class="b">760</b><span>公尺<br>西北側新陸地距岸</span></div>
  <div class="stat"><b class="b">495</b><span>公尺<br>東南側新陸地距岸</span></div>
</div>
<p class="note">資料：印尼地質局以 Sentinel 衛星影像比對；NOWnews、Antara 2026-09-25</p>"""

MEDIA = """
<div class="duo">
  <div class="card dark"><small>新聞標題</small><h3>「火山噴發後<br>冒出 2 座島？」</h3><p>讀者容易記住「新島」兩個字</p></div>
  <div class="card"><small>官方與專家怎麼說</small>
    <p><b>印尼地質局：</b>兩處隆起還不能確定是島或新火山，要實地查證。</p>
    <p><b>專家：</b>火山灰、岩塊、熔岩在淺海堆積，露出海面。</p>
    <p><b>BMKG：</b>必須比對噴發前後的地貌，才能下定論。</p></div>
</div>
<p class="motto">標題是一個主張，測量才是證據。</p>"""

PARTITION = """
<svg viewBox="0 0 1200 640" class="diagram">
  <defs>
    <marker id="ar" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#b04a3a"/></marker>
    <marker id="ab" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#2c6e91"/></marker>
  </defs>
  <rect width="1200" height="640" rx="24" fill="#d7e8f0"/>
  <path d="M40 470 C 400 500, 800 570, 1180 610" stroke="#2f3a3f" stroke-width="5" fill="none"/>
  <text x="60" y="565" class="dl">斜向隱沒（蘇門答臘外海）</text>
  <text x="860" y="632" class="dl">正向隱沒（爪哇外海）</text>
  <path d="M40 40 L 600 40 L 820 380 L 40 230 Z" fill="#c8b597" stroke="#6f4a35" stroke-width="3"/>
  <path d="M40 120 L 780 335 L 820 380 L 40 230 Z" fill="#b39a74"/>
  <text x="330" y="100" class="dl big">蘇門答臘</text>
  <path d="M40 120 L 780 335" stroke="#2f3a3f" stroke-width="4" stroke-dasharray="14 10"/>
  <text x="110" y="126" class="dl sm" transform="rotate(16.2 110 126)">大蘇門答臘斷層（右移，約 15 mm/yr）</text>
  <path d="M520 300 L 300 238" stroke="#b04a3a" stroke-width="12" fill="none" stroke-linecap="round" marker-end="url(#ar)"/>
  <text x="200" y="330" class="dl" style="fill:#b04a3a">弧前地塊往西北滑動</text>
  <path d="M875 400 L 1180 350 L 1180 540 L 925 560 Z" fill="#c8b597" stroke="#6f4a35" stroke-width="3"/>
  <text x="1010" y="475" class="dl big">爪哇</text>
  <path d="M800 470 L 890 510" stroke="#b04a3a" stroke-width="8" fill="none" stroke-linecap="round" marker-start="url(#ar)" marker-end="url(#ar)"/>
  <polygon points="848,412 832,440 864,440" fill="#f4d35e" stroke="#2f3a3f" stroke-width="3"/>
  <path d="M866 418 L 900 350" stroke="#2f3a3f" stroke-width="2"/>
  <text x="880" y="300" class="dl">喀拉喀托</text>
  <text x="880" y="336" class="dl sm">張裂地塹交會處</text>
  <path d="M560 630 L 600 555" stroke="#2c6e91" stroke-width="10" stroke-linecap="round" marker-end="url(#ab)"/>
  <text x="330" y="625" class="dl" style="fill:#2c6e91">印澳板塊聚合</text>
</svg>
<p class="note">示意圖，未依比例。資料：Harjono et al. 1991, Tectonics；Dahren et al. 2012, J. Petrology</p>"""

TIMELINE = """
<div class="timeline">
  <div class="ev"><b>1883</b><h4>大爆發</h4><p>火山猛烈爆發，留下海中的破火山口</p></div>
  <div class="ev"><b>1927</b><h4>誕生</h4><p>喀拉喀托之子在破火山口中冒出海面</p></div>
  <div class="ev dark"><b>2018</b><h4>側翼崩塌</h4><p>約 0.116 km³ 崩入海中；海嘯最高約 13 m，437 人罹難</p></div>
  <div class="ev"><b>2019–</b><h4>重建</h4><p>噴發轉為史托朗坡利式，新火山錐逐步長回</p></div>
  <div class="ev hot"><b>2026</b><h4>增生</h4><p>9 月噴發後新增 32.8 公頃，周邊出現兩處小隆起</p></div>
</div>
<p class="motto">成長 → 崩塌 → 再成長</p>"""

SCALE = """
<div class="duo scale">
  <div class="big-num"><b>≈ 13,000 年</b><span>板塊以每年約 58 mm 移動 760 公尺所需時間</span></div>
  <div class="big-num hot"><b>25 小時</b><span>這次噴發堆出 32.8 公頃新陸地</span></div>
</div>
<p class="motto">板塊提供岩漿來源與張裂通道；直接造出陸地的，是火山堆積。</p>"""

SEISMO = """
<div class="trio">
  <div class="card"><h4>訊號長什麼樣</h4><p>崩塌沒有產生強烈的短週期地動，但寬頻地震儀清楚記錄到週期 40–200 秒的長週期訊號。</p></div>
  <div class="card"><h4>為什麼沒有預警</h4><p>以地震規模與震源為基礎的判斷，難以即時辨識火山崩塌這類非典型海嘯源。</p></div>
  <div class="card"><h4>單力模型</h4><p>山體向西南滑落，地球受到向東北、峰值約 6.1×10¹¹ 牛頓、持續約 70 秒的反作用力。</p></div>
</div>
<p class="note">資料：Ye et al. 2020, Science Advances；Perttu et al. 2020, EPSL</p>"""

QUESTIONS = """
<ol class="questions">
  <li>巽他海峽位在隱沒帶上，為什麼卻是張裂環境？</li>
  <li>鬆散火山碎屑堆成的陸地會長久存在嗎？海浪侵蝕扮演什麼角色？</li>
  <li>回到開場：新島和板塊運動的關係，你的答案改變了嗎？</li>
</ol>
<p class="motto">不要只背地球的知識，要學會閱讀地球留下的證據。</p>"""

COVER = """
<div class="cover">
  <p class="kick">地震學 · 板塊構造學說 · 時事教材</p>
  <h1>喀拉喀托之子<br>長出的「新陸地」</h1>
  <p class="lede">從一則新聞，讀懂隱沒帶、海峽張裂與火山島的生命週期</p>
</div>"""

SCENES = [
    dict(kicker="", title="", body=COVER, cover=True, lines=[
        "2026 年 9 月，印尼的喀拉喀托之子火山，連續噴發了大約 25 小時。",
        "新聞標題寫著：火山噴發後，冒出兩座島？",
        "這支影片，我們用真實資料，從一則新聞，一路讀到板塊構造。",
    ]),
    dict(kicker="一、新聞事件", title="噴發 25 小時，陸地多了 32.8 公頃", body=STATS, lines=[
        "印尼地質局用 Sentinel 衛星影像比對，確認火山本體的陸地增加了約 32.8 公頃。",
        "在西北側距岸約 760 公尺、東南側約 495 公尺的地方，各出現一處新的隆起。",
        "警戒從第三級降為第二級，但仍然禁止靠近噴發中心 2 公里、新陸地 1 公里的範圍。",
    ]),
    dict(kicker="一、新聞事件 · 媒體識讀", title="「新島」？標題與官方說法的落差", body=MEDIA, lines=[
        "不過，官方並沒有說這是新島。",
        "地質局表示，這兩處隆起還不能確定是島嶼還是新火山，需要實地查證。",
        "專家認為，這是火山灰、岩塊和熔岩在淺海堆積，露出了海面。",
        "記住：標題是一個主張，測量才是證據。",
    ]),
    dict(kicker="二、板塊構造背景 · 全球定位", title="這段邊界在世界的哪裡？", body=img("20-global_plate_context.png"), lines=[
        "先把鏡頭拉遠。這張圖畫出全球的板塊邊界：紅色是聚合，藍色是張裂，灰色是錯動。",
        "黃色星號就是巽他海峽。它位在一條從喜馬拉雅延伸到印尼，再接上環太平洋火環的聚合帶上。",
    ]),
    dict(kicker="二、板塊構造背景 · 哪一種邊界", title="巽他板塊與澳洲板塊之間的隱沒帶", body=img("19-plate_boundary_map.png"), lines=[
        "放大來看。根據 Bird 在 2003 年發表的板塊邊界模型，這段邊界被分類為隱沒帶。",
        "紅色三角形的尖端，指向上覆的巽他板塊；另一側的印澳板塊，以每年大約 6 公分的速度隱沒下去。",
    ]),
    dict(kicker="二、板塊構造背景 · 真實資料", title="地震、火山與海溝", body=img("16-sunda_strait_map.png"), lines=[
        "疊上 2000 年以來、規模 4.5 以上的地震，顏色代表震源深度。",
        "地震沿著海溝密集分布；白色三角形的火山，排成一列與海岸平行的火山弧。",
        "喀拉喀托之子，就位在蘇門答臘和爪哇之間的海峽裡。",
    ]),
    dict(kicker="二、板塊構造背景 · 剖面", title="沿 A–B 線切開：隱沒板塊的證據", body=img("17-sunda_strait_section.png"), lines=[
        "沿著大致垂直海溝的 A、B 兩點，切一個剖面。",
        "地震從海溝附近的淺處，往東北一路變深，最深接近 600 公里。",
        "這條傾斜的地震帶，叫做班尼奧夫帶，就是隱沒板塊插入地函的證據。",
    ]),
    dict(kicker="二、板塊構造背景 · 巽他海峽", title="隱沒帶上的張裂", body=PARTITION, lines=[
        "但巽他海峽有個特別的地方：它位在隱沒帶上，卻是一個張裂的環境。",
        "爪哇外海是正向隱沒；到了蘇門答臘外海，卻轉成斜向隱沒。",
        "斜向的分量，由大蘇門答臘斷層吸收，把蘇門答臘的弧前地塊往西北拖。",
        "海峽因此被拉開。喀拉喀托就長在張裂地塹的交會處，岩漿很容易上升。",
    ]),
    dict(kicker="二、板塊構造背景 · 火山島的生命週期", title="成長、崩塌、再成長", body=TIMELINE, lines=[
        "喀拉喀托的歷史，是一個成長、崩塌、再成長的循環。",
        "1883 年的大爆發，留下海中的破火山口；1927 年，喀拉喀托之子冒出了海面。",
        "2018 年，火山側翼崩塌引發海嘯，造成 437 人罹難。之後，火山又重新長了回來。",
    ]),
    dict(kicker="三、教學應用 · 迷思釐清", title="新陸地是板塊「推」出來的嗎？", body=SCALE, lines=[
        "那麼，新陸地是板塊推出來的嗎？",
        "板塊一年只移動大約 6 公分；要走 760 公尺，需要超過一萬三千年。",
        "但這次噴發，只用了 25 小時。",
        "板塊提供岩漿來源與張裂通道；直接造出陸地的，是火山堆積。",
    ]),
    dict(kicker="三、教學應用 · 地震學連結", title="2018 年：地震儀看得到，預警卻沒響", body=SEISMO, lines=[
        "2018 年的崩塌，也給地震學上了一課。",
        "它沒有產生強烈的短週期震波，以地震規模為基礎的預警系統，沒有發出警報。",
        "寬頻地震儀卻記錄到長週期訊號：山體往西南滑落時，地球受到一個往東北的反作用力，這就是牛頓第三運動定律。",
    ]),
    dict(kicker="三、教學應用 · 連結臺灣", title="回到臺灣：同一套構造語彙", body=img("18-taiwan_map.png"), lines=[
        "回到臺灣。臺灣北邊有琉球海溝，南邊有馬尼拉海溝，兩條隱沒帶的方向相反。",
        "東北外海的沖繩海槽，也是隱沒帶附近的張裂，龜山島就在那裡。",
        "同樣是隱沒帶旁的張裂，巽他海峽來自斜向隱沒的應變分配，沖繩海槽則來自弧後擴張。",
    ]),
    dict(kicker="三、教學應用 · 討論", title="帶走三個問題", body=QUESTIONS, lines=[
        "最後，留下三個問題給你。",
        "巽他海峽位在隱沒帶上，為什麼卻是張裂環境？",
        "鬆散的火山碎屑堆成的陸地，會長久存在嗎？海浪侵蝕扮演什麼角色？",
        "回到開場：新島和板塊運動的關係，你的答案改變了嗎？",
        "不要只背地球的知識，要學會閱讀地球留下的證據。",
    ]),
]

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1920px;height:1080px;overflow:hidden;background:#f5f0e6;color:#1f2a33;
 font-family:'Noto Sans CJK TC',sans-serif;position:relative}
body::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 85% 10%,rgba(176,74,58,.08),transparent 40%),radial-gradient(circle at 10% 90%,rgba(44,110,145,.08),transparent 45%)}
.frame{position:absolute;inset:0;padding:56px 90px 0}
.kicker{font-size:28px;letter-spacing:.12em;color:#b04a3a;font-weight:700}
h2{font-family:'Noto Serif CJK TC',serif;font-size:62px;margin-top:10px;color:#1f2a33}
.stage{position:absolute;left:90px;right:90px;top:220px;bottom:190px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px}
.fig{max-width:100%;max-height:100%;object-fit:contain;background:#fff;padding:14px;border-radius:14px;box-shadow:0 18px 40px -20px rgba(31,42,51,.45)}
.sub{position:absolute;left:0;right:0;bottom:0;height:160px;background:rgba(31,42,51,.9);display:flex;align-items:center;justify-content:center;padding:0 120px}
.sub p{color:#fff;font-size:44px;line-height:1.35;text-align:center;font-weight:500}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:28px;width:100%}
.stat{background:#fbf8f2;border:2px solid #e3dccd;border-radius:20px;padding:40px 36px}
.stat b{display:block;font-size:96px;line-height:1}
.stat .t{color:#b04a3a}.stat .b{color:#2c6e91}
.stat span{display:block;font-size:32px;margin-top:18px;color:#3b4852;line-height:1.35}
.note{font-size:24px;color:#6b7680}
.duo{display:grid;grid-template-columns:1fr 1.5fr;gap:34px;width:100%}
.card{background:#fbf8f2;border:2px solid #e3dccd;border-radius:22px;padding:40px 44px}
.card small{font-size:28px;color:#2c6e91;font-weight:700}
.card h3{font-family:'Noto Serif CJK TC',serif;font-size:58px;margin:22px 0;line-height:1.3}
.card h4{font-size:40px;margin-bottom:18px;color:#1f2a33}
.card p{font-size:32px;line-height:1.5;margin-top:14px;color:#3b4852}
.card.dark{background:#1f2a33;border-color:#1f2a33}
.card.dark small{color:#e59a6d}.card.dark h3,.card.dark p{color:#f5f0e6}
.motto{font-family:'Noto Serif CJK TC',serif;font-size:46px;font-weight:700;color:#1f2a33}
.diagram{height:100%;max-height:610px}
.dl{font-family:'Noto Sans CJK TC';font-size:30px;fill:#1f2a33;font-weight:700}
.dl.big{font-size:42px}.dl.sm{font-size:26px}
.timeline{display:grid;grid-template-columns:repeat(5,1fr);gap:22px;width:100%}
.ev{background:#fbf8f2;border-top:10px solid #8a5a44;border-radius:18px;padding:30px 28px;min-height:360px}
.ev b{font-size:52px;color:#8a5a44}.ev h4{font-size:40px;margin:14px 0}.ev p{font-size:29px;line-height:1.5;color:#3b4852}
.ev.dark{background:#1f2a33;border-top-color:#e0703a}.ev.dark b{color:#e59a6d}.ev.dark h4,.ev.dark p{color:#f5f0e6}
.ev.hot{border-top-color:#b04a3a}.ev.hot b{color:#b04a3a}
.scale{grid-template-columns:1fr 1fr}
.big-num{background:#fbf8f2;border:2px solid #e3dccd;border-radius:22px;padding:50px}
.big-num b{display:block;font-size:110px;color:#2c6e91;line-height:1.1}
.big-num.hot b{color:#b04a3a}
.big-num span{display:block;font-size:34px;margin-top:20px;color:#3b4852;line-height:1.4}
.trio{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;width:100%}
.questions{font-size:48px;line-height:1.5;padding-left:70px;align-self:stretch}
.questions li{margin:14px 0;font-family:'Noto Serif CJK TC',serif}
.cover{position:absolute;inset:0;background:linear-gradient(135deg,#1c2530,#2a2a30 60%,#4a2e25);padding:0 140px;display:flex;flex-direction:column;justify-content:center}
.cover .kick{color:#e59a6d;font-size:34px;letter-spacing:.15em;font-weight:700}
.cover h1{font-family:'Noto Serif CJK TC',serif;color:#f5f0e6;font-size:128px;line-height:1.2;margin:30px 0}
.cover .lede{color:#d6d0c4;font-size:44px}
.progress{position:absolute;top:0;left:0;height:8px;background:#b04a3a}
"""


def slide_html(scene, line, progress):
    if scene.get("cover"):
        inner = scene["body"]
    else:
        inner = (f'<div class="frame"><p class="kicker">{scene["kicker"]}</p><h2>{scene["title"]}</h2></div>'
                 f'<div class="stage">{scene["body"]}</div>')
    subtitle = f'<div class="sub"><p>{line}</p></div>' if line else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'{inner}<div class="progress" style="width:{progress * 100:.1f}%"></div>{subtitle}</body></html>')


def audio_path(line):
    key = hashlib.sha1(f"{VOICE}|{RATE}|{line}".encode()).hexdigest()[:16]
    return BUILD / "audio" / f"{key}.mp3"


async def synthesize(lines):
    for line in lines:
        mp3 = audio_path(line)
        if not mp3.exists() or mp3.stat().st_size == 0:
            await edge_tts.Communicate(line, VOICE, rate=RATE).save(str(mp3))


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def vtt_time(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:06.3f}"


def screenshot(page, html, out, **kw):
    path = BUILD / "slides" / (out.stem + ".html")
    path.write_text(html, encoding="utf-8")
    page.goto(path.as_uri())
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(150)
    page.screenshot(path=str(out), **kw)


def main():
    for d in ("audio", "slides", "segments"):
        (BUILD / d).mkdir(parents=True, exist_ok=True)
    items = [(si, li, line) for si, sc in enumerate(SCENES) for li, line in enumerate(sc["lines"])]
    asyncio.run(synthesize([line for _, _, line in items]))

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for n, (si, li, line) in enumerate(items):
            screenshot(page, slide_html(SCENES[si], line, (n + 1) / len(items)),
                       BUILD / "slides" / f"{si:02d}_{li:02d}.png")
        screenshot(page, slide_html(SCENES[0], "", 0), POSTER, type="jpeg", quality=85)
        browser.close()

    segments, cues, t = [], ["WEBVTT", ""], 0.0
    for si, li, line in items:
        mp3, png = audio_path(line), BUILD / "slides" / f"{si:02d}_{li:02d}.png"
        seg = BUILD / "segments" / f"{si:02d}_{li:02d}.mp4"
        speech = duration(mp3)
        d = speech + LINE_TAIL + (SCENE_TAIL if li == len(SCENES[si]["lines"]) - 1 else 0)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", str(png),
                        "-i", str(mp3), "-af", "apad", "-t", f"{d:.3f}", "-c:v", "libx264", "-tune", "stillimage",
                        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                        "-ac", "2", str(seg)], check=True)
        segments.append(seg)
        cues += [f"{vtt_time(t)} --> {vtt_time(t + speech)}", line, ""]
        t += d

    listing = BUILD / "concat.txt"
    listing.write_text("".join(f"file '{s}'\n" for s in segments))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", "-movflags", "+faststart", str(VIDEO)], check=True)
    VTT.write_text("\n".join(cues), encoding="utf-8")
    print(f"{len(items)} 句、{t:.1f} 秒 → {VIDEO.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
