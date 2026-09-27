"""學生只改這個檔。另外兩個程式會讀這裡的設定。

區域寫成 [西, 東, 南, 北]，單位是度。
解析度的 m 是角分、s 是角秒：05m 比 02m 粗、下載比較快。
"""

from pathlib import Path

# 第一次練習維持 "taiwan"。做完再改成 "sunda"。
PRESET = "taiwan"

# 第一次先填 "05m"，確認整條流程跑得通，再改回 None（改用下面各範圍自己的解析度）。
RESOLUTION = None

# 模型的東西向寬度、地形起伏的高度、平底座的厚度。單位都是公釐（mm）。
# 這三個數字對得上網頁表格和範例 STL（臺灣：140 × 162.5 × 26 mm，海平面在底座以上 18.7 mm）。
# 真的要印、而且列印床較小：改成 WIDTH_MM = 80、RELIEF_MM = 13。
# 誇大仍約 10 倍，尺寸約 80 × 93 × 17 mm，通常兩到三小時。
# 140 mm 寬的範例加上 brim 後要確認放得進列印床，而且大約要印一整晚。全班共用一個，不要一人一個。
# 改了寬度或高度之後，海平面的公釐數會變，不要再對網頁上的 18.7 mm。
WIDTH_MM = 140
RELIEF_MM = 22
BASE_MM = 4

# 單邊超過這個點數就自動抽稀，避免 STL 大到切片軟體開很久。
# 噴嘴 0.4 mm、模型寬約 140 mm 時，250 個點已經比一層線還密。
MAX_POINTS = 250

PRESETS = {
    "taiwan": {
        "region": [118.2, 124.2, 20.0, 26.4],  # 含臺灣、琉球海溝西端、馬尼拉海溝北端
        "resolution": "02m",
        "title": "Taiwan and the nearby trenches",
    },
    "sunda": {
        "region": [102.0, 108.0, -8.5, -4.5],  # 巽他海峽、喀拉喀托之子、海溝
        "resolution": "02m",
        "title": "Sunda Strait and Anak Krakatau",
    },
}

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
