"""步驟 3：下載地形網格，畫成北方朝上的地形圖，並把網格存成 NetCDF。

只改 settings.py。在這個資料夾執行：

    python 01_plot_topography.py
    python 01_plot_topography.py --preset sunda
"""

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import settings as cfg  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="用 PyGMT 畫地形圖並存下網格")
    parser.add_argument("--preset", default=cfg.PRESET, choices=sorted(cfg.PRESETS))
    args = parser.parse_args()
    spec = cfg.PRESETS[args.preset]
    region = spec["region"]
    resolution = cfg.RESOLUTION or spec["resolution"]
    if len(region) != 4 or not (region[0] < region[1] and region[2] < region[3]):
        sys.exit("region 必須是 [西, 東, 南, 北]，而且西 < 東、南 < 北。")

    import pygmt

    print(f"步驟 3.1  下載地形  範圍={args.preset}  解析度={resolution}  區域={region}")
    print("         第一次下載會連到 GMT 資料伺服器，可能要幾分鐘。之後會用本機快取。")
    grid = pygmt.datasets.load_earth_relief(
        resolution=resolution, region=region, registration="gridline"
    )
    zmin = float(grid.min())
    zmax = float(grid.max())
    print(f"步驟 3.2  網格大小 {tuple(int(n) for n in grid.shape)}  高程 {zmin:.0f} m 到 {zmax:.0f} m")
    print(f"         高低差 {zmax - zmin:.0f} m。負值是海底，0 是海平面，正值是陸地。")

    cfg.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    nc_path = cfg.OUTPUT_DIR / f"{args.preset}_relief.nc"
    try:
        grid.to_netcdf(nc_path)
    except ValueError as exc:
        if "backend" not in str(exc):
            raise
        sys.exit("存不了 NetCDF。請在同一個 conda 環境安裝：  conda install -c conda-forge netcdf4")
    print(f"步驟 3.3  已存網格  {nc_path}")

    png_path = cfg.OUTPUT_DIR / f"{args.preset}_relief.png"
    print(f"步驟 3.4  繪圖      {png_path}")
    lat0 = (region[2] + region[3]) / 2
    x_km = (region[1] - region[0]) * 111.32 * math.cos(math.radians(lat0))
    scale_km = 100 if x_km < 500 else 200

    fig = pygmt.Figure()
    fig.grdimage(
        grid=grid,
        region=region,
        projection="M15c",
        cmap="geo",
        shading="+a-45+nt0.5",
        frame=["af", f"+t{spec['title']}"],
    )
    fig.coast(shorelines="0.35p,gray15", resolution="i")
    fig.colorbar(position="JMR+o0.7c/0c+w9c", frame=["a2000", "+lElevation (m)"])
    # pygmt 0.19 把比例尺和指北針分成兩個方法；舊版仍掛在 basemap 上。
    if hasattr(fig, "scalebar"):
        fig.scalebar(length=f"{scale_km}k", position="BL", fancy=True, label=True, scale_loc=lat0)
        fig.directional_rose(position="TL", width="1.8c", fancy=2, labels=True)
    else:
        fig.basemap(map_scale=f"jBL+c{lat0}+w{scale_km}k+f+lkm+o0.35c/0.35c")
        fig.basemap(rose="jTL+w1.8c+f2+l+o0.2c/0.2c")
    fig.savefig(png_path, dpi=200)

    print("完成。打開 PNG，確認三件事再往下做：")
    print("  1. 指北針朝上，東邊在右。")
    print("  2. 藍色是海、綠到棕色是陸地，色標單位是公尺。")
    print("  3. 你指得出海溝（最深的藍）和島嶼。")
    print("接著執行：  python 02_relief_to_stl.py")


if __name__ == "__main__":
    main()
