"""步驟 4：讀步驟 3 存下的地形網格，做成 3D 列印用的封閉 STL（單位公釐）。

    python 02_relief_to_stl.py
    python 02_relief_to_stl.py --preset sunda
    python 02_relief_to_stl.py --self-test

模型是一塊實心的地勢：最底是平的底座，四周是直牆，頂面是地形
（含海底）。海平面不是底座，程式會告訴你海平面在底座以上幾公釐。
北是 +Y，東是 +X。
"""

import argparse
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import settings as cfg  # noqa: E402


def load_grid(path):
    import xarray as xr

    grid = xr.open_dataarray(path)
    for name in ("lon", "lat"):
        if name not in grid.dims and name not in grid.coords:
            sys.exit(f"{path} 裡找不到座標 {name}。請重跑 01_plot_topography.py。")
    lon = np.asarray(grid.lon.values, dtype=float)
    lat = np.asarray(grid.lat.values, dtype=float)
    z = np.asarray(grid.values, dtype=float)
    # 轉成 z[緯度, 經度]，並且緯度由南往北，這樣列印時 +Y 是北。
    if grid.dims[-1] != "lon":
        z = np.moveaxis(z, grid.dims.index("lon"), -1)
    if lat[0] > lat[-1]:
        lat = lat[::-1]
        z = z[::-1, :]
    if lon[0] > lon[-1]:
        lon = lon[::-1]
        z = z[:, ::-1]
    return lon, lat, z


def coarsen(lon, lat, z, max_points):
    nlat, nlon = z.shape
    step = int(np.ceil(max(nlat, nlon) / max_points))
    if step <= 1:
        return lon, lat, z, 1
    lon, lat, z = lon[::step], lat[::step], z[::step, ::step]
    print(f"         單邊超過 {max_points} 點，已每 {step} 點取 1 點，剩下 {z.shape[0]} × {z.shape[1]}。")
    print("         要更細的模型就把 settings.py 的 MAX_POINTS 調大；檔案會變大、切片變慢。")
    return lon, lat, z, step


def _wall(tris, top_a, top_b, outward):
    """兩個頂點之間的直牆，法線朝外，底邊落在 z = 0。"""
    top_a = np.asarray(top_a, dtype=float)
    top_b = np.asarray(top_b, dtype=float)
    bot_a = np.array([top_a[0], top_a[1], 0.0])
    bot_b = np.array([top_b[0], top_b[1], 0.0])
    normal = np.cross(bot_b - bot_a, top_b - bot_a)
    if np.dot(normal, outward) >= 0:
        tris.extend(((bot_a, bot_b, top_b), (bot_a, top_b, top_a)))
    else:
        tris.extend(((bot_a, top_b, bot_b), (bot_a, top_a, top_b)))


def build_solid(lon, lat, elevation_m, width_mm, relief_mm, base_mm):
    """把高程網格做成實心三角網。回傳 (三角形, 給學生看的數字)。"""
    if np.isnan(elevation_m).any():
        sys.exit("網格裡有缺值。請把範圍改到有地形資料的地方，或換一個解析度。")
    zmin = float(elevation_m.min())
    zmax = float(elevation_m.max())
    span = zmax - zmin
    if span <= 0:
        sys.exit("這個範圍的高程沒有起伏，做不出地形。請把區域放大。")

    lat0 = float(np.mean(lat))
    x_km = np.deg2rad(lon[-1] - lon[0]) * 6371.0 * np.cos(np.deg2rad(lat0))
    y_km = np.deg2rad(lat[-1] - lat[0]) * 6371.0
    depth_mm = width_mm * (y_km / x_km)
    xs = np.linspace(0.0, width_mm, lon.size)
    ys = np.linspace(0.0, depth_mm, lat.size)
    # 最深處貼在底座頂面，最高處再高出 RELIEF_MM。
    zz = base_mm + (elevation_m - zmin) / span * relief_mm
    sea_mm = base_mm + (0.0 - zmin) / span * relief_mm

    nlat, nlon = zz.shape
    tris = []
    for i in range(nlat - 1):
        for j in range(nlon - 1):
            p00 = (xs[j], ys[i], zz[i, j])
            p10 = (xs[j + 1], ys[i], zz[i, j + 1])
            p11 = (xs[j + 1], ys[i + 1], zz[i + 1, j + 1])
            p01 = (xs[j], ys[i + 1], zz[i + 1, j])
            tris.append((p00, p10, p11))
            tris.append((p00, p11, p01))
            b00 = (xs[j], ys[i], 0.0)
            b10 = (xs[j + 1], ys[i], 0.0)
            b11 = (xs[j + 1], ys[i + 1], 0.0)
            b01 = (xs[j], ys[i + 1], 0.0)
            tris.append((b00, b01, b10))
            tris.append((b10, b01, b11))
    for j in range(nlon - 1):
        _wall(tris, (xs[j], ys[0], zz[0, j]), (xs[j + 1], ys[0], zz[0, j + 1]), (0, -1, 0))
        _wall(tris, (xs[j], ys[-1], zz[-1, j]), (xs[j + 1], ys[-1], zz[-1, j + 1]), (0, 1, 0))
    for i in range(nlat - 1):
        _wall(tris, (xs[0], ys[i], zz[i, 0]), (xs[0], ys[i + 1], zz[i + 1, 0]), (-1, 0, 0))
        _wall(tris, (xs[-1], ys[i], zz[i, -1]), (xs[-1], ys[i + 1], zz[i + 1, -1]), (1, 0, 0))

    verts = np.asarray(tris, dtype=np.float64)
    horizontal_scale = width_mm / (x_km * 1.0e6)  # 模型公釐 / 真實公釐
    vertical_scale = relief_mm / (span * 1000.0)
    report = {
        "x_km": x_km,
        "y_km": y_km,
        "zmin_m": zmin,
        "zmax_m": zmax,
        "span_m": span,
        "width_mm": width_mm,
        "depth_mm": depth_mm,
        "height_mm": base_mm + relief_mm,
        "base_mm": base_mm,
        "sea_mm": sea_mm,
        "exaggeration": vertical_scale / horizontal_scale,
        "unexaggerated_mm": span * 1000.0 * horizontal_scale,
        "triangles": len(tris),
        "points": (nlat, nlon),
    }
    return verts, report


def write_stl(path, verts, header_text):
    normals = np.cross(verts[:, 1] - verts[:, 0], verts[:, 2] - verts[:, 0])
    length = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, length, out=np.zeros_like(normals), where=length > 0)
    record = np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")])
    data = np.zeros(len(verts), dtype=record)
    data["n"] = normals
    data["v"] = verts
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(header_text.encode("ascii", "replace")[:80].ljust(80, b"\0"))
        handle.write(struct.pack("<I", len(verts)))
        handle.write(data.tobytes())


def is_closed(verts, tol_mm=1e-3):
    """每條邊正好被兩個三角形共用，才是切片軟體能修補的封閉模型。"""
    q = np.round(verts / tol_mm).astype(np.int64)
    edges = {}
    for tri in q:
        for a, b in ((0, 1), (1, 2), (2, 0)):
            ea = tuple(tri[a])
            eb = tuple(tri[b])
            key = (ea, eb) if ea <= eb else (eb, ea)
            edges[key] = edges.get(key, 0) + 1
    broken = sum(1 for count in edges.values() if count != 2)
    return broken == 0, broken


def print_report(report, closed, stl_path):
    ok = "是" if closed else "否，先不要拿去切片"
    print()
    print("========== 寫進學習單 ==========")
    print(f"真實範圍    東西 {report['x_km']:.0f} km，南北 {report['y_km']:.0f} km")
    print(f"高程        {report['zmin_m']:.0f} m 到 {report['zmax_m']:.0f} m，高低差 {report['span_m']:.0f} m")
    print(f"模型尺寸    {report['width_mm']:.1f} × {report['depth_mm']:.1f} × {report['height_mm']:.1f} mm")
    print(f"底座厚度    {report['base_mm']:.1f} mm")
    print(f"海平面      在底座以上 {report['sea_mm']:.1f} mm（底座是最深的海底，不是海平面）")
    print(f"垂直誇大    {report['exaggeration']:.1f} 倍")
    print(f"若不誇大    高低差只剩 {report['unexaggerated_mm']:.2f} mm，幾乎印不出來")
    print(f"網格        {report['points'][0]} × {report['points'][1]} 點，{report['triangles']} 個三角形")
    print(f"封閉        {ok}")
    print(f"檔案        {stl_path}")
    print("方向        +X 東、+Y 北。切片軟體裡請看座標軸，不要假設螢幕上方是北。")
    print("================================")


def run_self_test():
    # 西南低、東北高的斜坡。最高點必須落在 x 最大、y 最大的角。
    lon = np.linspace(121.0, 122.0, 6)
    lat = np.linspace(23.0, 24.0, 5)
    elevation = np.add.outer(np.linspace(0, 1000, lat.size), np.linspace(0, 1000, lon.size))
    verts, report = build_solid(lon, lat, elevation, width_mm=100, relief_mm=20, base_mm=4)
    closed, broken = is_closed(verts)
    peak = verts[:, :, 2].max()
    at_peak = verts.reshape(-1, 3)
    at_peak = at_peak[np.argmax(at_peak[:, 2])]
    checks = [
        ("封閉", closed and broken == 0),
        ("底在 z=0", abs(verts[:, :, 2].min()) < 1e-9),
        ("頂高等於底座加起伏", abs(peak - 24) < 1e-6),
        ("最高點在東北角", abs(at_peak[0] - 100) < 1e-6 and abs(at_peak[1] - report["depth_mm"]) < 1e-6),
        ("有誇大", report["exaggeration"] > 1),
        ("三角形數", report["triangles"] == 4 * 5 * 4 + 4 * (5 + 4)),
    ]
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("PASS  " if ok else "FAIL  ") + name)
    if failed:
        sys.exit("self-test 沒過：" + ", ".join(failed))
    print("self-test 通過")


def main():
    parser = argparse.ArgumentParser(description="地形網格轉成 3D 列印 STL")
    parser.add_argument("--preset", default=cfg.PRESET, choices=sorted(cfg.PRESETS))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--preview", action="store_true", help="另外存一張 3D 預覽 PNG（需要 matplotlib）")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return

    nc_path = cfg.OUTPUT_DIR / f"{args.preset}_relief.nc"
    if not nc_path.exists():
        sys.exit(f"找不到 {nc_path}。先執行：  python 01_plot_topography.py --preset {args.preset}")

    print(f"步驟 4.1  讀取網格  {nc_path}")
    lon, lat, z = load_grid(nc_path)
    lon, lat, z, _step = coarsen(lon, lat, z, cfg.MAX_POINTS)
    print("步驟 4.2  計算尺寸與垂直誇大，並建立封閉模型")
    verts, report = build_solid(lon, lat, z, cfg.WIDTH_MM, cfg.RELIEF_MM, cfg.BASE_MM)
    closed, broken = is_closed(verts)
    if not closed:
        sys.exit(f"模型沒有封閉（有 {broken} 條邊不是正好共用兩次）。不要拿去切片，請回報這個訊息。")

    stl_path = cfg.OUTPUT_DIR / f"{args.preset}_relief.stl"
    header = (
        f"units=mm exaggeration={report['exaggeration']:.2f}x "
        f"sea={report['sea_mm']:.2f}mm +X=east +Y=north"
    )
    write_stl(stl_path, verts, header)
    print_report(report, closed, stl_path)

    if args.preview:
        save_preview(lon, lat, z, cfg.OUTPUT_DIR / f"{args.preset}_relief_3d.png", report)
        print(f"預覽        {cfg.OUTPUT_DIR / f'{args.preset}_relief_3d.png'}")
    print("接著用 Cura、PrusaSlicer 或 Bambu Studio 打開這個 STL。尺寸要和上面的公釐數一致。")


def save_preview(lon, lat, z, path, report):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    lat0 = float(np.mean(lat))
    x_km = np.deg2rad(lon - lon[0]) * 6371.0 * np.cos(np.deg2rad(lat0))
    y_km = np.deg2rad(lat - lat[0]) * 6371.0
    xx, yy = np.meshgrid(x_km, y_km)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    step = max(1, max(z.shape) // 180)
    surface = ax.plot_surface(
        xx[::step, ::step], yy[::step, ::step], z[::step, ::step] / 1000.0,
        cmap="terrain", linewidth=0, antialiased=True,
    )
    ax.set_xlabel("east (km)")
    ax.set_ylabel("north (km)")
    ax.set_zlabel("elevation (km)")
    # 預覽的長寬高比跟要列印的模型一樣（含垂直誇大），不是真實比例。
    relief_mm = report["height_mm"] - report["base_mm"]
    ax.set_box_aspect((report["width_mm"], report["depth_mm"], relief_mm))
    ax.set_title(f"print preview, vertical exaggeration {report['exaggeration']:.1f}x")
    fig.colorbar(surface, shrink=0.6, label="elevation (km)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
