# 板塊構造學說：從地質證據推論板塊運動

**Plate Tectonics: Inferring Plate Motion from Geological Evidence**

三節課完整教材，讓學生從地震、火山、斷層與地形證據反推板塊運動，把板塊構造學說當成科學建模的案例，而不是三種邊界的背誦清單。

完整教學流程、提問、板書、參考答案與評量說明見：

[`板塊構造學說_三節課完整教材.md`](板塊構造學說_三節課完整教材.md)

## 互動式網頁

`index.html` 是這份教材的水彩風互動版本，整合了 `artifacts/` 中的 15 張證據圖：

- 中／英／雙語一鍵切換（CLIL）
- 地震分布圖疊上板塊邊界的揭示滑桿、地球分層點選
- 三個神秘區域與四個 Mystery Region 的證據推論選擇題
- 三種板塊邊界的動畫模型與因果鏈
- 證據實驗室：大陸拼合、海底擴張速率計算、隱沒帶地震、夏威夷熱點年齡計算
- 五個真實案例的 CER 寫作框與參考答案
- 時事案例「喀拉喀托之子冒出新島」：新聞查證分類題、火山島生命週期時間軸、隱沒／張裂／火山剖面示意圖、時間尺度計算器
- AI 第二輪驗證表單、Exit Tickets、探究護照進度
- 所有填寫內容存在瀏覽器 localStorage，可匯出為 Markdown 學習歷程

### 部署到 GitHub Pages

`.github/workflows/pages.yml` 會在每次推送到 `main` 時自動部署整個儲存庫根目錄。第一次使用時：

1. 到 repo 的 **Settings → Pages**，Source 選 **GitHub Actions**（工作流程含 `enablement: true`，多數情況下會自動開啟）。
2. 合併到 `main` 或到 **Actions → Deploy to GitHub Pages** 手動執行一次。
3. 網址為 `https://<帳號>.github.io/2026_utaipei_plate_tectonic/`。

本機預覽：在儲存庫根目錄執行 `python3 -m http.server 8000`，開啟 `http://localhost:8000/`。

## 適用對象與時數

- 大學地球物理通論、自然科學相關課程
- 可調整為高中自然科探究課程
- 3 節，每節 50 分鐘，共 150 分鐘

## 核心教學理念

課程依這條路徑進行：

**觀察 → 找規律 → 建立模型 → 解釋 → 預測 → 驗證 → 修正**

Observation → Pattern → Model → Explanation → Prediction → Test → Revision

學生先看真實世界的證據，再推論板塊如何運動。先觀察，再解釋；先說明形成原因，再辨認名稱。

## 學習目標

三節課結束後，學生能夠：

| 面向 | 學生能做到 |
|---|---|
| 知識 | 說明三種板塊邊界，以及它們與斷層、海溝、島弧、中洋脊、裂谷、盆地、山脈、地震深度與火山分布的關係 |
| 探究與建模 | 從地質證據建立模型，解釋已知現象，預測尚未提供的現象，並依新證據修正模型 |
| 科學論證 | 用 CER（Claim、Evidence、Reasoning）建立解釋 |
| CLIL | 用固定英文句型描述觀察、主張、證據、解釋與預測 |
| AI 素養 | 先建立自己的模型，再比較 AI 的解釋，並用證據判斷回答是否合理 |

## 三節課架構

| 節次 | 核心問題 | 主要活動 | 核心能力 |
|---|---|---|---|
| 第一節 | 世界上的地震、火山為什麼集中在特定地方？ | 全球觀察、三個神秘區域、建立三種板塊模型、身體動作模型 | 觀察、找規律、建模 |
| 第二節 | 為什麼不同板塊邊界形成不同地質構造？ | 日本海溝與島弧、喜馬拉雅山、東非裂谷、大西洋中洋脊／冰島、聖安地列斯斷層 | 證據、解釋、推理 |
| 第三節 | 如果模型正確，我們還能預測什麼？ | Mystery Region 小組挑戰、AI 第二輪驗證、模型修正、回到臺灣 | 預測、驗證、修正 |

第二節會修正一個常見過度簡化：不是所有聚合型邊界都一樣。洋洋、洋陸聚合可以隱沒並形成火山；陸陸碰撞（如喜馬拉雅）以地殼縮短與造山為主，活火山並不顯著。

第三節才開放使用 AI。學生須先交出自己的模型，再把觀察寫成 prompt，並保留原始模型、prompt、AI 回答、同意或不同意的理由、證據與修正後模型。

## 關鍵概念

| 板塊邊界 | 運動 | 應力 | 斷層 | 地震 | 火山 | 地形 |
|---|---|---|---|---|---|---|
| 張裂型 Divergent | 分離 | 張力 tension | 正斷層 | 淺源 | 常見 | 洋脊、裂谷、盆地 |
| 聚合型 Convergent | 聚合 | 壓力 compression | 逆斷層／逆衝斷層 | 淺至深 | 常見（碰撞帶除外） | 海溝、島弧、山脈 |
| 錯動型 Transform | 側向滑動 | 剪力 shear | 走向滑移斷層 | 淺源 | 通常很少 | 斷層谷、水平錯移 |

學生最終要建立的因果鏈：

**板塊運動 → 應力 → 岩石變形與斷層 → 地震／岩漿活動 → 地表地質構造**

## 課堂反覆使用的英文句型

- We observe that ______.
- We think this is a ______ boundary.
- Our evidence is ______.
- This can be explained by ______.
- Because the plates are moving ______, the crust experiences ______.
- If our model is correct, we should also observe ______.
- Based on the new evidence, we need to revise our model.

語言負擔可以壓到三個詞：**trench**（海溝）、**subduction**（隱沒）、**evidence**（證據）。

> A trench can provide evidence of subduction.

## 評量

| 評量 | 比例 | 看什麼 |
|---|---:|---|
| Observation | 20% | 能否從圖表找出有效證據 |
| Scientific model | 30% | 能否建立合理因果模型 |
| CER | 25% | Claim、Evidence、Reasoning 是否一致 |
| Model revision | 25% | 能否依新證據或 AI 回答修正模型 |

答案對不對不是唯一標準。評量看學生如何從證據走到結論。

建議繳交的學習歷程：最初判斷、初始模型圖、CER、AI prompt、AI 回答、對 AI 的評價、使用的證據、修改後模型、最終反思。

## 建議使用方式

1. 備課時先讀完整教材中的三節流程、板書因果鏈與 Exit Ticket 參考答案。
2. 第一節先展示全球地震、火山與地形，暫時不要先給板塊邊界圖。
3. 第二節依五個真實案例推進，並在喜馬拉雅案例明確要求修正模型。
4. 第三節分組進行 Mystery Region，完成預測後才使用 AI。
5. 結尾回到臺灣（中央山脈、西部麓山帶、縱谷、馬尼拉海溝、琉球海溝），讓學生看到真實板塊環境比單一圖示更複雜。
6. 延伸（選用）：以 2026 年 9 月喀拉喀托之子噴發新聞為時事案例，若想加入媒體識讀，可先做網頁中的新聞查證分類，再用時間尺度計算器打掉「新島是板塊推出來的」迷思，最後對照沖繩海槽／龜山島與呂宋島弧；投影片見 [`artifacts/喀拉喀托之子與板塊構造.pdf`](artifacts/喀拉喀托之子與板塊構造.pdf)；資料驅動的地圖與地震剖面版本見 [pygmt-map-lab 的案例：巽他海峽／喀拉喀托之子（2026）](https://github.com/oceanicdayi/pygmt-map-lab/tree/main/case-studies/2026-sunda-strait-krakatau)。

課程收束的一句話：

> Don't just memorize the Earth. Learn how to read the Earth.  
> 不要只背地球的知識，要學會閱讀地球留下的證據。

## 檔案

| 檔案 | 說明 |
|---|---|
| `板塊構造學說_三節課完整教材.md` | 三節課教學設計：學習目標、分鐘流程、案例、CER、Exit Ticket、評量與 AI 學習歷程 |
| `index.html`、`assets/` | 互動式網頁（HTML、水彩風 CSS、互動 JS） |
| `artifacts/` | 15 張地球物理證據圖：地震分布、板塊邊界、磁異常條紋、擴張速率、隱沒帶、熱點、大陸漂移復原、地球構造 |
| `artifacts/喀拉喀托之子與板塊構造.pdf` | 時事延伸投影片：2026 年 9 月喀拉喀托之子噴發新聞、巽他海峽的隱沒轉張裂構造、與台灣對照 |
| `.github/workflows/pages.yml` | GitHub Pages 自動部署 |
| `README.md` | 本說明 |

延伸案例（真實新聞事件對照）：[2026 巽他海峽・喀拉喀托之子](https://github.com/oceanicdayi/pygmt-map-lab/tree/main/case-studies/2026-sunda-strait-krakatau)，用 PyGMT 畫圖對照隱沒帶模型，收錄於姊妹專案 [pygmt-map-lab](https://github.com/oceanicdayi/pygmt-map-lab)。
