# 教學影片產生腳本

`build_krakatau_video.py` 產生互動網頁「九、時事案例」開頭的中文教學影片：

| 輸出 | 說明 |
|---|---|
| `../artifacts/21-krakatau_teaching_video.mp4` | 1080p、H.264/AAC，約 5 分半 |
| `../artifacts/21-krakatau_teaching_video.vtt` | WebVTT 字幕（網頁 `<track>` 用） |
| `../artifacts/21-krakatau_teaching_video_poster.jpg` | 影片封面 |

做法：每一句旁白是一張 1920×1080 投影片（HTML 截圖，字幕燒在畫面下方）加一段語音，最後用 ffmpeg 串成影片。畫面中的地圖直接取用 `../artifacts/16`–`20` 號圖（由 [pygmt-map-lab](https://github.com/oceanicdayi/pygmt-map-lab) 的 PyGMT 腳本產生）。

## 需要

- Python 套件：`pip install edge-tts playwright`，再 `playwright install chromium`
- `ffmpeg`（含 `ffprobe`）
- 字型：Noto Sans CJK TC、Noto Serif CJK TC（Ubuntu：`apt install fonts-noto-cjk`）
- 網路：語音由 edge-tts 呼叫微軟語音服務（聲音 `zh-TW-HsiaoChenNeural`）

## 執行

在 repo 根目錄：

```bash
python3 video/build_krakatau_video.py
```

中間檔放在 `video/build/`（不進版控）。語音依句子內容快取，改一句旁白只會重新合成那一句。

## PyGMT 地形圖轉 STL

`build_stl_video.py` 產生實作頁「從地形圖到 3D 列印」開頭的中文教學影片，說明同一份高程網格如何變成可切片的 STL：

| 輸出 | 說明 |
|---|---|
| `../artifacts/22-pygmt_stl_teaching_video.mp4` | 1080p、H.264/AAC |
| `../artifacts/22-pygmt_stl_teaching_video.vtt` | WebVTT 字幕 |
| `../artifacts/22-pygmt_stl_teaching_video_poster.jpg` | 影片封面 |

畫面使用 `pygmt_3dprint/example/` 的臺灣地形圖與列印預覽。中間檔在 `video/build_stl/`。

```bash
python3 video/build_stl_video.py
```

中文字型預設讀 `/tmp/cjkfonts/NotoSansTC.ttf` 與 `NotoSerifTC.ttf`，或用環境變數 `CJK_FONT_DIR` 指定目錄。找不到時改用系統的文泉驛微米黑。

可選的環境變數：

- `SSL_CERT_FILE`：在需要自訂 CA 的網路代理環境中，讓 edge-tts 使用這份憑證
- `CHROMIUM_PATH`：指定 Chromium 執行檔，取代 Playwright 預設下載的版本

## 修改內容

旁白與畫面都在腳本的 `SCENES`：每一段有 `kicker`（小標）、`title`（標題）、`body`（畫面 HTML 或 `img("圖檔名")`）與 `lines`（逐句旁白，同時也是字幕）。語速、聲音在 `VOICE`、`RATE`，句間停頓在 `LINE_TAIL`、`SCENE_TAIL`。
