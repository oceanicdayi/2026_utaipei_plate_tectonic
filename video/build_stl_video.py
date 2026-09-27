"""產生「PyGMT 地形圖 → 3D 列印 STL」的中文教學影片。

每一句旁白 = 一張 1920x1080 投影片（HTML 截圖，內嵌字幕）+ 一段 edge-tts 語音，
最後用 ffmpeg 串成 MP4，並輸出 WebVTT 字幕與封面圖到 ../artifacts/。

用法：python3 video/build_stl_video.py
需要：ffmpeg、playwright（含 Chromium）、edge-tts；合成語音需連網。
中文字型：環境變數 CJK_FONT_DIR 內放 NotoSansTC.ttf、NotoSerifTC.ttf；
找不到時改用系統的文泉驛微米黑。
修改旁白或畫面：編輯下方 SCENES；只有改過的句子會重新合成語音。
"""
import asyncio
import hashlib
import os
import subprocess
from pathlib import Path

import certifi

if os.environ.get("SSL_CERT_FILE"):
    certifi.where = lambda: os.environ["SSL_CERT_FILE"]
import edge_tts  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ART = ROOT / "artifacts"
EX = ROOT / "pygmt_3dprint" / "example"
BUILD = HERE / "build_stl"
VIDEO = ART / "22-pygmt_stl_teaching_video.mp4"
VTT = ART / "22-pygmt_stl_teaching_video.vtt"
POSTER = ART / "22-pygmt_stl_teaching_video_poster.jpg"

VOICE, RATE = "zh-TW-HsiaoChenNeural", "-4%"
LINE_TAIL = 0.28
SCENE_TAIL = 0.7


def font_face():
    candidates = [
        Path(os.environ["CJK_FONT_DIR"]) if os.environ.get("CJK_FONT_DIR") else None,
        Path("/tmp/cjkfonts"),
        HERE / "fonts",
    ]
    for folder in candidates:
        if folder and (folder / "NotoSansTC.ttf").exists() and (folder / "NotoSerifTC.ttf").exists():
            sans, serif = (folder / "NotoSansTC.ttf").as_uri(), (folder / "NotoSerifTC.ttf").as_uri()
            return (
                f"@font-face{{font-family:'Noto Sans CJK TC';src:url('{sans}') format('truetype');font-weight:100 900;}}"
                f"@font-face{{font-family:'Noto Serif CJK TC';src:url('{serif}') format('truetype');font-weight:100 900;}}"
            )
    return ""


def fig(name):
    return f'<img class="fig" src="{(EX / name).as_uri()}">'


PAIR = f"""
<div class="pair">
  <figure>{fig("taiwan_relief.png")}<figcaption>PyGMT 地形圖 · 北方朝上</figcaption></figure>
  <figure>{fig("taiwan_relief_3d.png")}<figcaption>同一個範圍的列印預覽 · 高度已誇大</figcaption></figure>
</div>"""

NUMBERS = """
<div class="trio">
  <div class="big-num"><b>613 km</b><span>真實的東西向寬度<br>縮成模型上的 140 mm</span></div>
  <div class="big-num hot"><b>2.2 mm</b><span>若不誇大，將近 10 km 的高低差<br>比一層列印還薄</span></div>
  <div class="big-num"><b>9.9 倍</b><span>這份 STL 的垂直誇大<br>坡度不能拿去量野外</span></div>
</div>
<p class="motto">水平照地圖縮，高度另外放大。兩件事要分開看。</p>"""

BLOCK = """
<svg viewBox="0 0 1200 560" class="diagram">
  <rect width="1200" height="560" rx="24" fill="#e7f0f5"/>
  <path d="M90 250 C 180 300, 230 390, 300 410 C 380 430, 430 250, 520 160 C 600 80, 700 120, 780 200 C 860 280, 980 340, 1110 300 L 1110 470 L 90 470 Z" fill="#c4ad8a" stroke="#6f4a35" stroke-width="4"/>
  <path d="M90 250 C 180 300, 230 390, 300 410 C 380 430, 430 250, 520 160 C 600 80, 700 120, 780 200 C 860 280, 980 340, 1110 300" fill="none" stroke="#8a5a44" stroke-width="8"/>
  <rect x="90" y="470" width="1020" height="48" fill="#8a5a44"/>
  <line x1="70" y1="250" x2="1130" y2="250" stroke="#2c6e91" stroke-width="4" stroke-dasharray="14 10"/>
  <text x="140" y="232" class="dl sea">海平面 0 m · 底座以上 18.7 mm</text>
  <text x="640" y="108" class="dl big">地形頂面</text>
  <text x="150" y="348" class="dl">海溝在低處</text>
  <text x="250" y="502" class="dl light">底座 4 mm · 最深的海底貼在這裡，不是海平面</text>
</svg>
<p class="note">示意，未依比例。東是 +X，北是 +Y。四周直牆加平底，模型才封閉。</p>"""

STEPS = """
<div class="quad">
  <div class="card"><small>1</small><h4>換座標</h4><p>經緯度換成公釐。東是 +X，北是 +Y。南北長度照真實比例。</p></div>
  <div class="card"><small>2</small><h4>貼底座</h4><p>最深的海底放在 4 mm 厚的底座上。海平面浮在半空，不是底面。</p></div>
  <div class="card"><small>3</small><h4>拉高度</h4><p>從最深到最高再抬高 22 mm。這一步造成約 10 倍的垂直誇大。</p></div>
  <div class="card"><small>4</small><h4>封起來</h4><p>頂面是地形，四周補直牆，底面封死。每條邊正好被兩個三角形共用。</p></div>
</div>"""

TERMINAL = """
<div class="term">
  <p class="cmd">$ python 01_plot_topography.py</p>
  <p class="cmd">$ python 02_relief_to_stl.py</p>
  <p class="gap"></p>
  <p>模型尺寸　　140.0 × 162.5 × 26.0 mm</p>
  <p>海平面　　　底座以上 18.7 mm</p>
  <p class="ok">垂直誇大　　9.9 倍　　　封閉：是</p>
</div>
<p class="note">學生只改 settings.py。這兩行分別畫圖、轉成 STL。四個數字抄進學習單。</p>"""

SLICER = """
<ol class="questions slicer">
  <li>單位選公釐。尺寸要和終端機一致，差超過 1 mm 就停。</li>
  <li>不要只拉高。要改大小，三個方向一起縮。</li>
  <li>底座平貼平台。第一層應是完整的長方形。</li>
  <li>看座標軸找北，印完在北側標一個 N。</li>
</ol>
<p class="motto">Cura、PrusaSlicer、Bambu Studio 都可以。</p>"""

LIMIT = """
<div class="duo">
  <div class="card dark"><small>模型做得到</small><h3>海溝、山脈、島嶼的相對高低</h3><p>這是百萬年尺度的地形，一格大約 3 到 4 公里。</p></div>
  <div class="card"><small>模型做不到</small><h3>32.8 公頃的新陸地</h3><p>不到 1 平方公里，比一格還小。那是 25 小時的火山堆積，不在這份網格裡。</p></div>
</div>
<p class="motto">看得到的是地形。看不到的，不要說成板塊推出來的島。</p>"""

COVER = """
<div class="cover">
  <p class="kick">實作 · PyGMT · 3D 列印</p>
  <h1>地形圖<br>變成 STL</h1>
  <p class="lede">同一份高程網格，怎麼變成列印機讀得懂的檔案</p>
</div>"""

SCENES = [
    dict(kicker="", title="", body=COVER, cover=True, lines=[
        "這支影片只做一件事。",
        "把 PyGMT 畫好的地形圖，變成 3D 列印用的 STL 檔。",
    ]),
    dict(kicker="你會得到什麼", title="一張圖，和一個模型", body=PAIR, lines=[
        "左邊是地形圖，右邊是同一個範圍的模型。",
        "圖給人看。STL 給列印機讀。來源是同一份高程網格。",
    ]),
    dict(kicker="步驟一 · 先看懂圖", title="臺灣與旁邊的海溝", body=fig("taiwan_relief.png"), lines=[
        "這張圖的範圍是臺灣，和旁邊的海溝。北方朝上，東邊在右。",
        "藍色是海底，棕色是山。最深大約六千五百公尺，最高大約三千兩百公尺。",
    ]),
    dict(kicker="步驟二 · 為什麼不能照真實比例印", title="不誇大的話，山只有兩公釐", body=NUMBERS, lines=[
        "真實的東西向大約六百一十三公里，模型把它縮成一百四十公釐。",
        "高度若用同樣的比例，將近一萬公尺的高低差，只剩兩點二公釐。",
        "比一層列印還薄。所以程式把高度放大了九點九倍。",
        "模型上的坡因此比較陡，不能拿來量野外的坡度。",
    ]),
    dict(kicker="步驟三 · 網格怎麼變成實心塊", title="底座、直牆、封起來", body=BLOCK, lines=[
        "轉檔的時候，最深的海底貼在四公釐厚的底座上。",
        "海平面不是底座。在這份模型裡，它大約在底座以上十八點七公釐。",
        "頂面是地形，四周補上直牆，底面封死，才是封閉的實心塊。",
    ]),
    dict(kicker="步驟四 · 程式做的四件事", title="座標、底座、高度、封閉", body=STEPS, lines=[
        "拆開來看，程式做四件事。",
        "第一，經緯度換成公釐，東是 X，北是 Y。",
        "第二和第三，海底貼上底座，再把高低差抬高二十二公釐。",
        "第四，每條邊正好被兩個三角形共用。終端機要寫「封閉：是」。",
    ]),
    dict(kicker="步驟五 · 你實際下的指令", title="只改設定，跑這兩行", body=TERMINAL, lines=[
        "學生只改 settings.py。畫圖、轉檔，就是這兩行。",
        "跑完把四個數字抄下來：尺寸、海平面、誇大倍數，還有封閉是不是「是」。",
    ]),
    dict(kicker="步驟六 · 切片軟體", title="打開 STL 之後對四件事", body=SLICER, lines=[
        "用 Cura、PrusaSlicer 或 Bambu Studio 打開，單位選公釐。",
        "尺寸要是一百四十乘一百六十二點五、高二十六公釐。差超過一公釐，先不要印。",
        "不要只把模型拉高。底座平貼平台，第一層應該是一個完整的長方形。",
        "看座標軸找北方，印完在北側標一個 N。",
    ]),
    dict(kicker="最後 · 這個模型做不到的事", title="新陸地不在這份網格裡", body=LIMIT, lines=[
        "還有一件事，這個模型做不到。",
        "兩角分的格子大約三到四公里。三十二點八公頃的新陸地，比一格還小。",
        "海溝是百萬年的地形。那塊新陸地，是二十五小時的火山堆積。不要混在一起。",
    ]),
]

CSS = font_face() + """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1920px;height:1080px;overflow:hidden;background:#f5f0e6;color:#1f2a33;
 font-family:'Noto Sans CJK TC','WenQuanYi Micro Hei',sans-serif;position:relative}
body::before{content:"";position:absolute;inset:0;background:
 radial-gradient(circle at 85% 10%,rgba(176,74,58,.08),transparent 40%),
 radial-gradient(circle at 10% 90%,rgba(44,110,145,.08),transparent 45%)}
.frame{position:absolute;inset:0;padding:48px 80px 0}
.kicker{font-size:28px;letter-spacing:.12em;color:#b04a3a;font-weight:700}
h2{font-family:'Noto Serif CJK TC','Noto Serif TC',serif;font-size:58px;margin-top:8px;color:#1f2a33}
.stage{position:absolute;left:80px;right:80px;top:200px;bottom:180px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px}
.fig{max-width:100%;max-height:100%;object-fit:contain;background:#fff;padding:12px;border-radius:14px;box-shadow:0 18px 40px -20px rgba(31,42,51,.45)}
.sub{position:absolute;left:0;right:0;bottom:0;height:150px;background:rgba(31,42,51,.92);display:flex;align-items:center;justify-content:center;padding:0 100px}
.sub p{color:#fff;font-size:40px;line-height:1.35;text-align:center;font-weight:500}
.note{font-size:26px;color:#5c6770}
.motto{font-family:'Noto Serif CJK TC',serif;font-size:40px;font-weight:700;color:#1f2a33;text-align:center}
.pair{display:grid;grid-template-columns:1.15fr .85fr;gap:28px;width:100%;height:100%;align-items:center}
.pair figure{display:flex;flex-direction:column;align-items:center;gap:12px;min-height:0;height:100%;justify-content:center}
.pair .fig{max-height:560px}
.pair figcaption{font-size:28px;color:#3b4852;font-weight:700}
.card{background:#fbf8f2;border:2px solid #e3dccd;border-radius:22px;padding:32px 36px}
.card small{font-size:42px;color:#b04a3a;font-weight:700;font-family:'Noto Serif CJK TC',serif}
.card h3{font-family:'Noto Serif CJK TC',serif;font-size:48px;margin:12px 0;line-height:1.3}
.card h4{font-size:36px;margin:8px 0 10px}
.card p{font-size:28px;line-height:1.45;color:#3b4852}
.card.dark{background:#1f2a33;border-color:#1f2a33}
.card.dark small{color:#e59a6d}
.card.dark h3,.card.dark p{color:#f5f0e6}
.duo{display:grid;grid-template-columns:1fr 1fr;gap:28px;width:100%}
.quad{display:grid;grid-template-columns:1fr 1fr;gap:22px;width:100%}
.trio{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;width:100%}
.big-num{background:#fbf8f2;border:2px solid #e3dccd;border-radius:22px;padding:36px 32px}
.big-num b{display:block;font-size:84px;color:#2c6e91;line-height:1.05;font-family:'Noto Serif CJK TC',serif}
.big-num.hot b{color:#b04a3a}
.big-num span{display:block;font-size:30px;margin-top:16px;color:#3b4852;line-height:1.4}
.diagram{width:100%;max-height:520px}
.dl{font-family:'Noto Sans CJK TC','WenQuanYi Micro Hei',sans-serif;font-size:28px;fill:#1f2a33;font-weight:700}
.dl.big{font-size:36px}
.dl.sm{font-size:26px}
.dl.sea{fill:#2c6e91}
.dl.light{fill:#f5f0e6}
.term{background:#1f2a33;color:#f5f0e6;border-radius:22px;padding:42px 56px;width:100%}
.term p{font-size:36px;line-height:1.55;font-family:'WenQuanYi Micro Hei Mono','Noto Sans CJK TC',monospace}
.term .cmd{color:#e7b089}
.term .ok{color:#b7d7a8}
.term .gap{height:18px}
.questions{font-size:42px;line-height:1.45;padding-left:64px;width:100%}
.questions li{margin:16px 0;font-family:'Noto Serif CJK TC',serif}
.cover{position:absolute;inset:0;background:linear-gradient(135deg,#1c2530,#24343c 55%,#3d3228);padding:0 140px;display:flex;flex-direction:column;justify-content:center}
.cover .kick{color:#e59a6d;font-size:34px;letter-spacing:.16em;font-weight:700}
.cover h1{font-family:'Noto Serif CJK TC',serif;color:#f5f0e6;font-size:120px;line-height:1.15;margin:28px 0}
.cover .lede{color:#d6d0c4;font-size:42px}
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
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def vtt_time(t):
    minutes, seconds = divmod(t, 60)
    return f"{int(minutes):02d}:{seconds:06.3f}"


def screenshot(page, html, out, **kw):
    path = BUILD / "slides" / (out.stem + ".html")
    path.write_text(html, encoding="utf-8")
    page.goto(path.as_uri())
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(180)
    page.screenshot(path=str(out), **kw)


def main():
    for name in ("audio", "slides", "segments"):
        (BUILD / name).mkdir(parents=True, exist_ok=True)
    items = [(si, li, line) for si, scene in enumerate(SCENES) for li, line in enumerate(scene["lines"])]
    asyncio.run(synthesize([line for _, _, line in items]))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for n, (si, li, line) in enumerate(items):
            screenshot(page, slide_html(SCENES[si], line, (n + 1) / len(items)),
                       BUILD / "slides" / f"{si:02d}_{li:02d}.png")
        screenshot(page, slide_html(SCENES[0], "", 0), POSTER, type="jpeg", quality=86)
        browser.close()

    segments, cues, t = [], ["WEBVTT", ""], 0.0
    for si, li, line in items:
        mp3 = audio_path(line)
        png = BUILD / "slides" / f"{si:02d}_{li:02d}.png"
        seg = BUILD / "segments" / f"{si:02d}_{li:02d}.mp4"
        speech = duration(mp3)
        length = speech + LINE_TAIL + (SCENE_TAIL if li == len(SCENES[si]["lines"]) - 1 else 0)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", str(png),
            "-i", str(mp3), "-af", "apad", "-t", f"{length:.3f}",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(seg),
        ], check=True)
        segments.append(seg)
        cues += [f"{vtt_time(t)} --> {vtt_time(t + speech)}", line, ""]
        t += length

    listing = BUILD / "concat.txt"
    listing.write_text("".join(f"file '{segment}'\n" for segment in segments))
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-c", "copy", "-movflags", "+faststart", str(VIDEO),
    ], check=True)
    VTT.write_text("\n".join(cues), encoding="utf-8")
    print(f"{len(items)} 句、{t:.1f} 秒 → {VIDEO.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
