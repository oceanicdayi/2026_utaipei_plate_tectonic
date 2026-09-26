# Claude 專案內容分析紀錄

> 本檔案記錄 Claude 對本儲存庫（2026_utaipei_plate_tectonic）的完整閱讀過程與分析結果。
> 產生時間：2026-09-26　分析者：Claude（claude-sonnet-5）

---

## 一、專案一句話定位

這是一套**《板塊構造學說：從地質證據推論板塊運動》**的大學／高中地球科學教材，核心方法論是「不背誦三種板塊邊界，而是從地震、火山、斷層、地形等真實證據反推板塊運動」。內容以繁體中文為主、搭配 CLIL（Content and Language Integrated Learning）雙語英文句型，並包含一個可直接部署到 GitHub Pages 的水彩風互動網頁版本。

三節課的探究路徑：

```
Observation → Pattern → Model → Explanation → Prediction → Test → Revision
觀察 → 找規律 → 建立模型 → 解釋 → 預測 → 驗證 → 修正
```

---

## 二、儲存庫檔案總覽

```
.
├── .nojekyll                          # 告訴 GitHub Pages 不要用 Jekyll 處理
├── .github/workflows/pages.yml        # 推到 main 時自動部署到 GitHub Pages
├── README.md                          # 專案總覽（含教學理念、架構、部署說明）
├── 板塊構造學說_三節課完整教材.md      # 教材本體，1188 行，三節課逐分鐘教案
├── index.html                         # 互動網頁（615 行）
├── assets/
│   ├── app.js                         # 網頁互動邏輯（352 行，純 vanilla JS）
│   └── style.css                      # 水彩風視覺設計（395 行）
├── artifacts/
│   ├── 01–15-*.png                    # 15 張地球物理教科書證據圖
│   ├── readme.md                       # 只有一行 "readme"（幾乎空白）
│   └── 喀拉喀托之子與板塊構造.pdf       # 4.0 MB，補充閱讀 PDF
└── grok_bot_generate/
    ├── README.md                       # CLIL 雙語教材包說明＋線上資源清單
    ├── readme.md                       # 只有一行 "readme"（幾乎空白，大小寫重複檔名）
    ├── 01_bilingual_glossary.md         # 中英對照字彙表
    ├── 02_clil_lesson_outline.md        # 2–3 堂 CLIL 教案大綱
    ├── 03_student_worksheet.md          # 學習單（含解答）
    └── This_Dynamic_Planet_Teaching_Companion.pdf  # 6.6 MB，USGS 官方教學配套 PDF
```

Git 歷史：從 `e87f190 Initial commit` 到最新的 `c832017 Add files via upload`，共約 10 個 commit，內容由「初始 README」逐步擴充到「CLIL 雙語互動網頁」，顯示這是一個持續迭代中的教學專案（PR #1、#2、#3 皆已合併）。

---

## 三、核心教材內容分析：`板塊構造學說_三節課完整教材.md`

### 3.1 整體結構

| 節次 | 核心問題 | 主要活動 | 核心能力 |
|---|---|---|---|
| 第一節 | 世界上的地震、火山為什麼集中在特定地方？ | 全球觀察、三個神秘區域（Mystery A/B/C）、建立三種板塊模型、身體動作模型 | Observation、Pattern、Model |
| 第二節 | 為什麼不同板塊邊界形成不同地質構造？ | 五個真實案例（日本、喜馬拉雅、東非裂谷、大西洋中洋脊／冰島、聖安地列斯）＋ CER | Evidence、Explanation、Reasoning |
| 第三節 | 如果模型正確，我們還能預測什麼？ | Mystery Region 小組挑戰（A–D）、AI 第二輪驗證、模型修正、回到臺灣 | Prediction、Test、Revision |

### 3.2 教學法設計亮點

1. **先觀察、後命名**：教師刻意「先不展示板塊邊界圖」，也不先問「三種邊界是什麼」，而是先給證據讓學生自己畫箭頭、推運動方向。板書標語 `Observation ≠ Explanation` 貫穿全課。
2. **CER 科學論證框架**（Claim–Evidence–Reasoning）：每個案例都要求學生用固定三段式建立解釋，並且明確指出「答案對不對不是唯一標準，更重要的是從證據到結論的推理過程」。
3. **模型修正的認知衝突設計**：
   - 喜馬拉雅山案例刻意打破「聚合型邊界＝火山」的過度簡化，引入 oceanic–continental / oceanic–oceanic / continental–continental 三種聚合型的差異。
   - AI 驗證環節故意用「冰島火山很多但不是聚合型」當反例，逼學生承認「單一證據不能決定板塊環境，需要多重證據」。
4. **AI 素養設計具備正確的使用順序**：規則是「先建模、才能問 AI」（`Do not ask AI for the answer before you build your own model`），學生需保留 prompt、AI 回答、同意/不同意理由、修正後模型 —— 這是把 AI 當作「第二個驗證者」而非「答案來源」，是本教材在 AI 融入教學上最值得注意的設計。
5. **CLIL 語言負擔控制得宜**：不要求大量英文單字，而是把整堂課壓縮成 3 個關鍵詞（trench, subduction, evidence）與 7 個句型鷹架（We observe that…／We think this is…／This can be explained by…／If our model is correct, we should also observe…等）。
6. **收束到臺灣本土情境**：最後回扣中央山脈、西部麓山帶、花東縱谷、馬尼拉海溝、琉球海溝，讓學生看到「真實地球比單一模型複雜」（雙隱沒帶＋碰撞帶並存於同一島嶼）。

### 3.3 評量設計

| 評量項目 | 比例 | 核心關注點 |
|---|---:|---|
| Observation | 20% | 能否從圖表找出有效證據 |
| Scientific model | 30% | 能否建立合理因果模型 |
| CER | 25% | Claim / Evidence / Reasoning 是否一致 |
| Model revision | 25% | 能否依新證據或 AI 回答修正模型 |

建議繳交學習歷程共 9 項（最初判斷 → 初始模型圖 → CER → AI Prompt → AI 回答 → 對 AI 評價 → 使用的證據 → 修改後模型 → 最終反思），目的是讓評分者看到「thinking process」而非只看「final answer」。

### 3.4 核心因果鏈（全課最關鍵板書）

```
Plate motion 板塊運動
   ↓
Stress 應力
   ↓
Rock deformation / Faulting 岩石變形／斷層
   ↓
Earthquakes / Magma generation 地震／岩漿活動
   ↓
Surface geological structures 地表地質構造
```

三種邊界對照表：

| Plate Boundary | Motion | Stress | Fault | Earthquakes | Volcanoes | Landforms |
|---|---|---|---|---|---|---|
| Divergent 張裂型 | apart | tension | normal | shallow | common | ridge, rift, basin |
| Convergent 聚合型 | together | compression | reverse/thrust | shallow–deep | often（碰撞帶除外） | trench, arc, mountains |
| Transform 錯動型 | slide past | shear | strike-slip | shallow | usually few | fault valleys, offsets |

---

## 四、互動網頁分析：`index.html` + `assets/app.js` + `assets/style.css`

### 4.1 技術架構

- **純靜態網站**：無框架、無建置流程，HTML + vanilla JS（IIFE 模式）+ CSS，可直接以 `python3 -m http.server` 本機預覽，或透過 `.github/workflows/pages.yml` 自動部署到 GitHub Pages。
- **狀態管理**：所有使用者輸入（文字框、checkbox、蓋章進度）皆透過一個極簡的 `store` 物件存在瀏覽器 `localStorage`（key 前綴 `rte:`），完全不上傳、不需後端，貼合教育場景的隱私需求。
- **視覺風格**：水彩／手繪風，使用 SVG `feTurbulence` + `feDisplacementMap` 濾鏡（`#wobble`, `#wobble-soft`, `#paper-edge`）製造紙張邊緣手繪感；字型搭配 Caveat（手寫體）、Nunito、Noto Sans/Serif TC。

### 4.2 九大互動區塊（對應 README 的章節）

1. **`#observe` 觀察**：地震分布圖 vs 板塊邊界圖的滑桿疊圖（reveal slider），checkbox 讓學生勾選觀察到的現象，並可點選地球分層（crust / lithosphere / asthenosphere / mesosphere / core）查看說明。
2. **`#mysteries` 三個神秘區域**：Mystery A/B/C 給證據、學生選邊界類型，答對才顯示因果鏈說明；三題全對會自動蓋章。
3. **`#model` 建模**：三個分頁（Divergent/Convergent/Transform）搭配 SVG 動畫（板塊、火山、地震點、箭頭）與對應因果鏈文字。
4. **`#evidence` 證據實驗室**：四個抽屜（大陸拼合、海底擴張、隱沒帶地震、熱點軌跡），內含兩個「迷你實驗」計算器：
   - 海底擴張速率計算：`distance = half-rate × age`，可選三個真實洋脊（East Pacific Rise 44 mm/yr、Juan de Fuca 29 mm/yr、Reykjanes 10 mm/yr）。
   - 夏威夷熱點年齡計算：依 10 cm/yr 板塊速率反推年齡，並在 >3400 km（皇帝海山鏈轉折處）與 2300–2600 km（Midway，實測 ~27 Ma）給出額外提示。
5. **`#cases` 真實案例與 CER**：五個案例（日本、喜馬拉雅、東非裂谷、大西洋中洋脊/冰島、聖安地列斯），每個案例有證據清單、引導問題、學生 CER 填寫欄，以及展開才看到的參考答案（`<details>`）與「twist」延伸討論。填完 ≥2 案例的 CER 會自動蓋章。
6. **`#predict` Mystery Region 小組挑戰**：Region A–D，答對顯示標準答案與後續預測提示；四區全對自動蓋章。
7. **`#ai` AI 第二輪驗證**：一個完整表單（原始模型 → prompt → AI 回答 → 同意/不同意 → 證據 → 修正模型 → 反思），並附「判斷 AI 回答的三個問題」檢核清單。
8. **`#taiwan` 回到臺灣**：手繪風臺灣地圖 SVG，列出中央山脈／西部麓山帶／花東縱谷／琉球海溝／馬尼拉海溝五個構造單元。
9. **`#language` CLIL 語言角**：可點擊發音（Web Speech API `speechSynthesis`）與複製（Clipboard API）的句型與單字卡。
10. **`#exit` / `#assess`**：三份 Exit Ticket（對應三節課）＋ 評量比例視覺化（rubric bar）。

### 4.3 「探究護照」（Inquiry Passport）機制

- 共 9 個蓋章項目：5 個手動按鈕蓝章（observe / model / evidence / ai / language / taiwan，共 6 個）+ 3 個自動蓋章（mysteries / cases / predict，依完成度自動觸發）。
  - 實際計算：`total = document.querySelectorAll(".stamp-btn").length + AUTO_STAMPS.length`，頁首會顯示 `count/total`（例如 `0/9`），提供學生進度感。
- 完成後可一鍵**匯出 Markdown 學習歷程**（`exportPortfolio()`），整份檔案包含：觀察筆記、三個神秘區域完成狀態、五個案例的 CER、四個 Mystery Region 的預測、AI 驗證表單七欄、三份 Exit Ticket 答案、護照蓋章統計，命名為 `plate-tectonics-portfolio-<日期>.md`，直接對應教材第十章「AI 對話也列入學習歷程」的要求。這是整個網頁與紙本教材呼應最緊密的功能。

### 4.4 圖片來源

`artifacts/` 中的 15 張圖對應教科書 Fig. 1.5–1.27，footer 已列出原始出處：Wegener 1922、Köppen & Wegener 1924、Bullard et al. 1965、Smith & Hallam 1970、Van der Voo 1993、Barazangi & Dorman 1969、DeMets et al. 1990、Heirtzler et al. 1966、Pitman & Heirtzler 1966、Vine 1966、Isacks & Molnar 1969、Crough & Judy 1980、Van Andel 1992、Wilson 1963、Dalrymple et al. 1977（僅供教學使用）。

---

## 五、輔助資料夾：`grok_bot_generate/`

這個資料夾看起來是另一套（可能由 Grok 產生、後補充進本專案的）CLIL 雙語教材包，內容與主教材風格略有不同（更偏傳統教案格式，而非探究式）：

- **`01_bilingual_glossary.md`**：19 個核心詞彙的中英對照表（plate tectonics、lithosphere、subduction、hotspot、ring of fire 等）＋ 5 個課堂句型。
- **`02_clil_lesson_outline.md`**：標準 CLIL 4Cs 教案（Content/Communication/Cognition/Culture），依 Engage-Explore-Explain-Elaborate-Evaluate 分三個 period，含臺灣連結（Philippine Sea Plate vs Eurasian Plate、花蓮地震）。
- **`03_student_worksheet.md`**：配對題＋填空題＋簡答題＋地圖任務的傳統學習單，附教師解答。
- **`README.md`**：整理了 8 個外部線上資源連結（CLIL Prime、Genially、IPRASE、USGS This Dynamic Planet/Earth、NOAA、中央氣象署地震測報中心、教育雲 x2、字彙練習網站），並建議使用順序。
- **`This_Dynamic_Planet_Teaching_Companion.pdf`**（6.6 MB）：USGS 官方教學配套（含 Wegener 拼圖活動等），是本資料夾唯一的大型附件。

**與主教材的關係**：主教材（三節課完整版）是「探究建模」取向、以 CER 為核心；`grok_bot_generate/` 這一包更像是傳統詞彙／教案／學習單的補充包，且提供了不少外部資源連結可搭配使用。兩者目前在文件上沒有互相引用，屬於平行存在的兩套素材。

---

## 六、觀察到的小問題（僅記錄，未做修改）

1. `artifacts/readme.md` 與 `grok_bot_generate/readme.md` 內容都只有一行 `readme`，幾乎是空檔案，可能是誤上傳的佔位檔。
2. `grok_bot_generate/` 內同時有 `README.md`（有實質內容）與 `readme.md`（幾乎空白）兩個大小寫不同的檔案，在大小寫不敏感的檔案系統（例如某些 Windows 設定）上可能衝突或造成混淆。
3. 主教材與 `grok_bot_generate/` 的兩套素材彼此沒有交叉連結（例如 README.md 主文件未提及 `grok_bot_generate/` 資料夾），對於不熟悉儲存庫結構的使用者可能不容易發現後者。
4. `index.html` 版本號以 `?v=3` 手動管理快取（`style.css?v=3`、`app.js?v=3`），日後更新樣式/腳本時需記得手動遞增版本號，否則使用者瀏覽器可能吃到快取的舊檔案。

以上僅為紀錄觀察，不影響教材本身的教學設計品質；如需修正，可再另行處理。

---

## 七、總結評語

這是一套設計完整、教學法紮實的探究式地球科學教材：

- **內容深度**：涵蓋板塊構造學說的完整證據鏈（大陸拼合、海底擴張、隱沒帶地震、熱點軌跡），不是泛泛而談的三邊界介紹。
- **教學法先進**：以「觀察→建模→預測→驗證→修正」的科學建模循環貫穿三節課，並將 AI 使用規範化為「先建模、後驗證」的第二輪檢核工具，是目前 K-12／大學基礎課程中少見的、對 AI 素養有具體操作程序的設計。
- **雙語（CLIL）與本土化兼顧**：語言負擔控制精簡（3 個關鍵字＋7 個句型），並在結尾回扣臺灣真實構造環境，兼顧國際教材語言與在地認同。
- **技術實作完整**：互動網頁不只是教材的「電子版」，而是把探究護照、CER 表單、計算器、匯出學習歷程等評量機制都做成可操作的功能，使評量真正能看到學生的「thinking process」而非「final answer」。

主要可留意的地方是兩套素材（主教材 vs `grok_bot_generate/`）之間缺乏交叉引用，以及幾個近乎空白的 `readme.md` 佔位檔案，這些屬於文件整理層級的小事，不影響教材核心品質。
