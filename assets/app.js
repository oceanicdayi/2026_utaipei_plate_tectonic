/* Reading the Earth — interactive inquiry page
   All state lives in localStorage on the student's device. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const store = {
    get(k, d) { try { const v = localStorage.getItem("rte:" + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem("rte:" + k, JSON.stringify(v)); } catch { /* private mode */ } },
    clear() { Object.keys(localStorage).filter(k => k.startsWith("rte:")).forEach(k => localStorage.removeItem(k)); }
  };
  const bi = (zh, en) => `<span class="bi"><span class="zh">${zh}</span><span class="en">${en}</span></span>`;
  const toast = (msg) => { const t = $("#toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove("show"), 1800); };

  /* ---------------- language mode ---------------- */
  const modeBtns = $$(".lang-toggle button");
  function setMode(m) {
    document.body.className = "mode-" + m;
    document.documentElement.lang = m === "en" ? "en" : "zh-Hant";
    modeBtns.forEach(b => b.classList.toggle("active", b.dataset.mode === m));
    store.set("mode", m);
  }
  modeBtns.forEach(b => b.addEventListener("click", () => setMode(b.dataset.mode)));
  setMode(store.get("mode", "both"));

  /* ---------------- passport (progress) ---------------- */
  const stamps = new Set(store.get("stamps", []));
  const AUTO_STAMPS = ["mysteries", "cases", "predict"]; // earned by completing activities, no button
  const total = $$(".stamp-btn").length + AUTO_STAMPS.length;
  $("#passport-total").textContent = total;
  function renderStamps() {
    $$(".stamp-btn").forEach(b => b.classList.toggle("stamped", stamps.has(b.dataset.stamp)));
    $("#passport-count").textContent = stamps.size;
  }
  $$(".stamp-btn").forEach(b => b.addEventListener("click", () => {
    if (stamps.has(b.dataset.stamp)) stamps.delete(b.dataset.stamp); else { stamps.add(b.dataset.stamp); toast("Stamped ✓ 蓋章"); }
    store.set("stamps", [...stamps]); renderStamps();
  }));
  renderStamps();

  /* ---------------- persist any textarea / checkbox ---------------- */
  function bindPersist(root = document) {
    $$("textarea, input[type=checkbox], input[type=radio]", root).forEach((el, i) => {
      if (el.dataset.bound) return;
      const isCheck = el.type === "checkbox" || el.type === "radio";
      let key = el.id || el.name || el.dataset.key;
      if (!key) { if (el.type !== "checkbox") return; key = "check-" + i; }
      if (el.type === "radio") key += ":" + el.value;
      const k = "field:" + key;
      const saved = store.get(k, null);
      if (saved !== null) { if (isCheck) el.checked = saved; else el.value = saved; }
      el.addEventListener("input", () => store.set(k, isCheck ? el.checked : el.value));
      el.dataset.bound = "1";
    });
  }

  /* ---------------- observe: reveal slider ---------------- */
  const rr = $("#reveal-range"), rt = $("#reveal-top"), ro = $("#reveal-out");
  const applyReveal = () => { rt.style.opacity = rr.value / 100; ro.textContent = rr.value + "%"; };
  rr.addEventListener("input", applyReveal); applyReveal();

  /* ---------------- earth layers ---------------- */
  const layerInfo = {
    crust: ["地殼很薄：海洋 6–8 km（玄武岩、輝長岩），大陸 38–40 km（較輕的花崗岩質）。它是板塊「最上面那層皮」，不是板塊本身。", "The crust is thin: 6–8 km under oceans (basalt, gabbro), 38–40 km under continents (lighter, granitic). It is the skin of a plate, not the plate itself."],
    litho: ["岩石圈 = 地殼 + 最上部剛性地函，厚 70–150 km。板塊就是岩石圈的碎片；斷層和地震發生在這裡。", "Lithosphere = crust + rigid uppermost mantle, 70–150 km thick. Plates are pieces of lithosphere; faults and earthquakes live here."],
    asth: ["軟流圈部分熔融、可以緩慢流動。板塊「漂」在它上面。隱沒的板塊上半部被拉入這層低強度區，所以呈拉張（見證據實驗室 Fig. 1.18）。", "The asthenosphere is partially molten and flows slowly. Plates ride on it. The upper part of a subducting slab is pulled into this weak layer, so it is in extension (see Evidence Lab, Fig. 1.18)."],
    meso: ["下部地函半固態、可塑；強度較高。隱沒板塊下段頂到這裡會被壓縮，甚至折斷。深源地震最深約 670–700 km，正是這個轉換帶。", "The lower mantle is semi-solid and plastic but stronger. The lower slab meets it and is compressed, sometimes breaking off. The deepest earthquakes (~670–700 km) coincide with this transition."],
    core: ["外核是液態鐵鎳，產生地磁場——這才有磁異常條紋可以記錄海底擴張。內核固態。", "The fluid iron–nickel outer core generates the magnetic field, which is why sea-floor spreading leaves magnetic stripes. The inner core is solid."]
  };
  $$("#layers .layer").forEach(b => b.addEventListener("click", () => {
    $$("#layers .layer").forEach(x => x.classList.toggle("active", x === b));
    const [zh, en] = layerInfo[b.dataset.key];
    $("#layer-info").innerHTML = `<span class="zh">${zh}</span><span class="en">${en}</span>`;
  }));

  /* ---------------- mysteries ---------------- */
  const boundaries = {
    divergent: { sym: "← →", en: "Divergent boundary", zh: "張裂型板塊邊界" },
    convergent: { sym: "→ ←", en: "Convergent boundary", zh: "聚合型板塊邊界" },
    transform: { sym: "↑ ↓", en: "Transform boundary", zh: "錯動型板塊邊界" }
  };
  const chains = {
    divergent: [["Plate motion ← →", "板塊分離"], ["Tension", "張力"], ["Normal fault", "正斷層"], ["Rift / basin / ridge", "裂谷／盆地／洋脊"], ["Shallow earthquakes", "淺源地震"], ["Volcanism", "岩漿上升、火山"]],
    convergent: [["Plate motion → ←", "板塊聚合"], ["Compression", "壓力"], ["Reverse / thrust fault", "逆斷層／逆衝斷層"], ["Subduction or collision", "隱沒或碰撞"], ["Shallow-to-deep earthquakes", "淺至深源地震"], ["Trench / arc / mountains", "海溝／島弧／山脈"]],
    transform: [["Plate motion ↑ ↓", "板塊側向錯動"], ["Shear stress", "剪力"], ["Strike-slip fault", "走向滑移斷層"], ["Shallow earthquakes", "淺源地震"], ["Horizontal displacement", "水平錯移"], ["Few volcanoes", "火山很少"]]
  };
  const mysteries = [
    { id: "A", answer: "divergent", ev: [["shallow earthquakes", "淺源地震"], ["normal faults", "正斷層"], ["volcanoes", "火山"], ["GPS: the two sides move apart", "GPS：兩側彼此遠離"]],
      why: ["兩側遠離 → 張力 → 正斷層 → 地塊下沉成裂谷／盆地 → 岩漿上升。", "Moving apart → tension → normal faults → blocks drop to form a rift/basin → magma rises."] },
    { id: "B", answer: "convergent", ev: [["trench", "海溝"], ["volcanic arc", "火山弧"], ["earthquakes from shallow to deep", "地震由淺到深"]],
      why: ["一側板塊往下鑽：海溝標出下沉處，地震沿著斜面愈來愈深，板塊釋放的水讓地函熔融，火山排成弧。老師先不說「subduction」，讓你自己找到能同時解釋三件事的過程。", "One plate dives under the other: the trench marks where it bends down, earthquakes deepen along the slab, released water melts the mantle and volcanoes line up in an arc. Find the one process that explains all three observations."] },
    { id: "C", answer: "transform", ev: [["shallow earthquakes", "淺源地震"], ["horizontal displacement", "水平位移"], ["strike-slip fault", "走向滑移斷層"], ["few volcanoes", "火山很少"]],
      why: ["板塊擦身而過：剪力造成走向滑移斷層，地震淺而多，但沒有大量隱沒或岩漿生成，所以火山少。", "Plates slide past each other: shear makes strike-slip faults, many shallow earthquakes, but little subduction or melting, so few volcanoes."] }
  ];
  $("#mystery-grid").innerHTML = mysteries.map(m => `
    <article class="card mystery" data-id="${m.id}">
      <h3>Mystery ${m.id}</h3>
      <ul class="evidence">${m.ev.map(([en, zh]) => `<li>${en}<small>${zh}</small></li>`).join("")}</ul>
      <p class="hint">${bi("地底下發生了什麼事？先畫箭頭，再選。", "What is happening underground? Draw the arrows, then choose.")}</p>
      <div class="choices">${Object.entries(boundaries).map(([k, b]) => `<button class="choice" data-pick="${k}"><b>${b.sym}</b>${bi(b.zh, b.en)}</button>`).join("")}</div>
      <div class="feedback"></div>
    </article>`).join("");
  $$(".mystery").forEach(card => {
    const m = mysteries.find(x => x.id === card.dataset.id);
    const fb = $(".feedback", card);
    const solved = store.get("mystery:" + m.id, false);
    const show = (pick) => {
      $$(".choice", card).forEach(c => { c.classList.remove("right", "wrong"); if (c.dataset.pick === pick) c.classList.add(pick === m.answer ? "right" : "wrong"); });
      if (pick === m.answer) {
        fb.className = "feedback ok";
        fb.innerHTML = `<b>${boundaries[pick].sym} ${boundaries[pick].en}</b><br>${bi(m.why[0], m.why[1])}`;
        store.set("mystery:" + m.id, true); checkMysteries();
      } else {
        fb.className = "feedback no";
        fb.innerHTML = bi("再看一次證據。哪一條證據和你的選擇矛盾？", "Look at the evidence again. Which line contradicts your choice?");
      }
    };
    $$(".choice", card).forEach(c => c.addEventListener("click", () => show(c.dataset.pick)));
    if (solved) show(m.answer);
  });
  function checkMysteries() {
    if (mysteries.every(m => store.get("mystery:" + m.id, false)) && !stamps.has("mysteries")) {
      stamps.add("mysteries"); store.set("stamps", [...stamps]); renderStamps(); toast("Mysteries solved ✓ 三個區域全部解開");
    }
  }
  checkMysteries();

  /* ---------------- model builder ---------------- */
  const anim = $("#plate-anim"), chainEl = $("#chain");
  function setModel(k) {
    anim.dataset.model = k;
    $$(".model-tab").forEach(t => t.classList.toggle("active", t.dataset.model === k));
    chainEl.innerHTML = chains[k].map(([en, zh], i) => `${i ? "<i>↓</i>" : ""}<span>${en}<small>${zh}</small></span>`).join("");
  }
  $$(".model-tab").forEach(t => t.addEventListener("click", () => setModel(t.dataset.model)));
  setModel("divergent");

  /* ---------------- evidence lab drawers ---------------- */
  $$(".drawer-tab").forEach(t => t.addEventListener("click", () => {
    $$(".drawer-tab").forEach(x => x.classList.toggle("active", x === t));
    $$(".drawer").forEach(d => d.classList.toggle("active", d.id === "drawer-" + t.dataset.drawer));
  }));
  // spreading calculator
  const ridge = $("#ridge-select"), ageR = $("#age-range"), ageO = $("#age-out"), spreadOut = $("#spread-result"), dot1 = $("#ridge-dot"), dot2 = $("#ridge-dot-2");
  function calcSpread() {
    const rate = +ridge.value, age = +ageR.value; // mm/yr × Ma = km
    const km = rate * age; ageO.textContent = age.toFixed(1) + " Ma";
    spreadOut.innerHTML = `≈ ${Math.round(km)} km <small>from the ridge axis (each side) · 距洋脊軸兩側各 ${Math.round(km)} km · 全寬 ${Math.round(2 * km)} km</small>`;
    const pct = Math.min(48, km / 180 * 48); dot1.style.left = (50 + pct) + "%"; dot2.style.left = (50 - pct) + "%";
  }
  ridge.addEventListener("change", calcSpread); ageR.addEventListener("input", calcSpread); calcSpread();
  // hawaii calculator
  const hR = $("#hawaii-range"), hO = $("#hawaii-out"), hRes = $("#hawaii-result");
  function calcHawaii() {
    const km = +hR.value; hO.textContent = km + " km";
    const ma = km / 100; // 10 cm/yr = 100 km/Ma
    let note = "";
    if (km > 3400) note = ` <small>圖上這一段（皇帝海山鏈）年齡比直線預測更老，且方向轉折——板塊運動方向曾改變。 · Beyond the bend the chain is older than the line predicts and changes direction: the plate motion changed.</small>`;
    else if (km >= 2300 && km <= 2600) note = ` <small>Midway 實測約 27 Ma · measured ≈ 27 Ma</small>`;
    hRes.innerHTML = `≈ ${ma.toFixed(1)} Ma${note}`;
  }
  hR.addEventListener("input", calcHawaii); calcHawaii();

  /* ---------------- real cases (lesson 2) ---------------- */
  const cases = [
    { id: "japan", zh: "日本海溝＋日本島弧", en: "Japan Trench & island arc", fig: "artifacts/06-plate_tectonic_model.png",
      ev: [["Japan Trench", "日本海溝"], ["volcanic arc", "火山弧"], ["earthquakes become deeper inland", "地震往內陸愈來愈深"]],
      qs: [["Why is there a trench?", "為什麼有海溝？"], ["Why are volcanoes located behind the trench?", "為什麼火山在海溝後方？"], ["Why do earthquakes become deeper?", "為什麼地震愈來愈深？"]],
      cer: ["This is a convergent boundary with subduction.", "We observe a trench, a volcanic arc, and earthquakes from shallow to deep.", "One plate is subducting beneath another plate; the slab bends down at the trench, earthquakes trace the slab (Wadati–Benioff zone), and water released from the slab melts the mantle to feed the arc."],
      cerZh: ["這是有隱沒作用的聚合型邊界。", "我們觀察到海溝、火山弧，以及由淺到深的地震。", "一個板塊隱沒到另一個板塊之下；板塊在海溝處下彎，地震沿板塊排成斜面，板塊釋放的水使地函熔融，供應火山弧。"],
      twist: ["島弧是怎麼來的？", "海洋板塊隱沒到另一海洋板塊之下（oceanic–oceanic）→ 岩漿 → 火山排成一串島：日本、馬里亞納。", "Why a chain of islands? Oceanic–oceanic convergence → magma → a curved line of volcanic islands: Japan, the Marianas."] },
    { id: "himalaya", zh: "喜馬拉雅山", en: "The Himalayas", fig: null,
      ev: [["very high mountains", "極高的山脈"], ["earthquakes", "地震"], ["thrust faults", "逆衝斷層"], ["few active volcanoes", "很少活火山"]],
      qs: [["If convergent boundaries produce volcanoes, why are volcanoes not dominant here?", "如果聚合型邊界會產生火山，為什麼這裡火山不顯著？"]],
      cer: ["This is a convergent boundary, but a continent–continent collision rather than subduction.", "Thrust faults, crustal shortening, very high mountains and earthquakes, but few volcanoes.", "Continental lithosphere is too buoyant to subduct easily; compression shortens and thickens the crust, building mountains instead of a volcanic arc."],
      cerZh: ["這是聚合型邊界，但屬於陸陸碰撞而非隱沒。", "逆衝斷層、地殼縮短、極高山脈與地震，但很少火山。", "大陸岩石圈太輕、不易隱沒；壓力使地殼縮短、加厚，形成山脈而不是火山弧。"],
      twist: ["模型修正", "不是所有聚合型邊界都相同：洋—陸、洋—洋可以隱沒；陸—陸比較不容易隱沒。A model may need to be revised when new evidence appears.", "Model revision: not all convergent boundaries are the same. Oceanic–continental and oceanic–oceanic can subduct; continental–continental resists. A model may need to be revised when new evidence appears."] },
    { id: "eafrica", zh: "東非裂谷", en: "East African Rift", fig: null,
      ev: [["normal faults", "正斷層"], ["shallow earthquakes", "淺源地震"], ["volcanoes", "火山"], ["elongated basins", "狹長盆地"]],
      qs: [["Why is Africa splitting apart?", "為什麼非洲在裂開？"], ["If extension continues for millions of years, what may happen?", "如果拉張持續幾百萬年，會發生什麼？"]],
      cer: ["The region is undergoing extension.", "Normal faults, shallow earthquakes, volcanoes, and rift basins.", "When the crust is pulled apart, normal faults form and blocks move downward, forming basins; mantle material rises and generates magma."],
      cerZh: ["這個區域正在受到拉張。", "正斷層、淺源地震、火山與裂谷盆地。", "地殼受到拉張時會形成正斷層；部分地塊下沉形成裂谷盆地，深部物質上升則可能產生岩漿。"],
      twist: ["預測", "裂谷 → 海水進入 → 狹長海域 → 新海洋。紅海就是走到一半的例子。", "Prediction: rift → seawater enters → a long narrow sea → a new ocean. The Red Sea is this process half-way through."] },
    { id: "atlantic", zh: "大西洋中洋脊／冰島", en: "Mid-Atlantic Ridge / Iceland", fig: "artifacts/03-magnetic_anomaly_age.png",
      ev: [["a mountain range in the middle of the ocean", "海洋中央的山脈"], ["symmetric magnetic stripes", "對稱的磁異常條紋"], ["shallow earthquakes", "淺源地震"], ["volcanoes (Iceland)", "火山（冰島）"]],
      qs: [["Why is there a mountain range in the middle of the ocean?", "為什麼海洋中間有一條山脈？"]],
      cer: ["This is a divergent boundary where new oceanic crust forms.", "A ridge along the ocean centre, shallow earthquakes, volcanism, and magnetic anomalies that are symmetric about the ridge and get older with distance.", "Plate divergence lets the mantle rise and melt; magma builds new crust at the axis, which then moves away on both sides, so the sea floor is youngest at the ridge and records past magnetic reversals as stripes."],
      cerZh: ["這是形成新海洋地殼的張裂型邊界。", "海洋中央的洋脊、淺源地震、火山活動，以及以洋脊為中心對稱、愈遠愈老的磁異常條紋。", "板塊分離使地函上升熔融；岩漿在軸部形成新地殼並向兩側移開，所以海底在洋脊最年輕，並以條紋記錄過去的地磁反轉。"],
      twist: ["冰島", "冰島是中洋脊露出海面的特殊案例。它有很多火山，但不是聚合型——這是稍後檢驗「火山＝聚合」的反例。", "Iceland is a mid-ocean ridge exposed above sea level. Many volcanoes, but not convergent: a counter-example for 'volcanoes = convergent' later on."] },
    { id: "sanandreas", zh: "聖安地列斯斷層", en: "San Andreas Fault", fig: null,
      ev: [["shallow earthquakes", "淺源地震"], ["horizontal offset (rivers, fences, roads)", "水平錯移（河流、圍籬、道路）"], ["strike-slip faults", "走向滑移斷層"], ["few volcanoes", "火山很少"]],
      qs: [["Why are there many earthquakes but few volcanoes?", "為什麼地震很多、火山卻很少？"]],
      cer: ["This is a transform boundary.", "Shallow earthquakes, horizontal offsets and strike-slip faults, with few volcanoes.", "The Pacific and North American plates slide past each other; shear stress is released in strike-slip earthquakes, but there is no large-scale subduction or melting to make volcanoes."],
      cerZh: ["這是錯動型邊界。", "淺源地震、水平錯移與走向滑移斷層，火山很少。", "太平洋板塊與北美板塊擦身而過；剪力以走向滑移地震釋放，但沒有大量隱沒或熔融，所以沒有火山。"],
      twist: ["對照", "把聖安地列斯和日本放在一起：都地震很多，但一個有火山、一個沒有。單一證據（地震）無法決定板塊環境。", "Compare with Japan: both have many earthquakes, one has volcanoes and the other does not. A single line of evidence cannot decide the setting."] }
  ];
  const caseTabs = $("#case-tabs"), casePanel = $("#case-panel");
  caseTabs.innerHTML = cases.map((c, i) => `<button class="case-tab ${i ? "" : "active"}" data-case="${c.id}">${i + 1}. ${c.en}<small>${c.zh}</small></button>`).join("");
  function renderCase(id) {
    const c = cases.find(x => x.id === id);
    $$(".case-tab").forEach(t => t.classList.toggle("active", t.dataset.case === id));
    casePanel.innerHTML = `
      <div>
        <div class="case-head"><h3>${c.en}</h3><div class="sub-en">${c.zh}</div></div>
        <ul class="evidence">${c.ev.map(([en, zh]) => `<li>${en}<small>${zh}</small></li>`).join("")}</ul>
        <ul class="questions">${c.qs.map(([en, zh]) => `<li>${en}<small>${zh}</small></li>`).join("")}</ul>
        ${c.fig ? `<figure class="polaroid tilt-l case-fig"><img src="${c.fig}" alt="${c.en}"></figure>` : `<div class="board"><strong>Draw the section underground.</strong><span class="zh">小組先畫出地下剖面圖，再寫 CER。</span></div>`}
      </div>
      <div>
        <form class="cer-form" data-case="${c.id}">
          <label><b>Claim</b>${bi("主張：這是什麼板塊環境？", "What plate setting is this?")}<textarea name="cer-${c.id}-claim" rows="2" placeholder="We think this is a … boundary."></textarea></label>
          <label><b>Evidence</b>${bi("證據：你觀察到什麼？", "What do you observe?")}<textarea name="cer-${c.id}-evidence" rows="2" placeholder="We observe …"></textarea></label>
          <label><b>Reasoning</b>${bi("推理：為什麼這些證據支持主張？", "Why does the evidence support the claim?")}<textarea name="cer-${c.id}-reasoning" rows="3" placeholder="This can be explained by …"></textarea></label>
        </form>
        <details class="answer">
          <summary>${bi("展開參考 CER（寫完再看）", "Open the model CER (after writing yours)")}</summary>
          <div class="cer-mini">
            <div><b>Claim</b>${bi(c.cerZh[0], c.cer[0])}</div>
            <div><b>Evidence</b>${bi(c.cerZh[1], c.cer[1])}</div>
            <div><b>Reasoning</b>${bi(c.cerZh[2], c.cer[2])}</div>
          </div>
        </details>
        <div class="twist"><b>${c.twist[0]}</b><br>${bi(c.twist[1], c.twist[2])}</div>
      </div>`;
    bindPersist(casePanel);
  }
  $$(".case-tab").forEach(t => t.addEventListener("click", () => renderCase(t.dataset.case)));
  renderCase(cases[0].id);
  casePanel.addEventListener("input", () => {
    const filled = cases.filter(c => ["claim", "evidence", "reasoning"].every(k => (store.get(`field:cer-${c.id}-${k}`, "") || "").trim().length > 5)).length;
    if (filled >= 2 && !stamps.has("cases")) { stamps.add("cases"); store.set("stamps", [...stamps]); renderStamps(); toast("CER ✓ 完成兩個案例"); }
  });

  /* ---------------- mystery regions (lesson 3) ---------------- */
  const regions = [
    { id: "A", ev: [["deep ocean trench", "深海溝"], ["volcanic arc", "火山弧"], ["earthquakes 0–600 km", "地震深度 0–600 km"], ["compression", "壓力"]], answer: "convergent", label: ["Subduction zone", "隱沒帶"],
      predict: ["reverse faults, an inclined seismic zone dipping away from the trench, an accretionary wedge, a back-arc basin", "逆斷層、從海溝向內陸傾斜的地震帶、增積岩體、弧後盆地"] },
    { id: "B", ev: [["normal faults", "正斷層"], ["crustal thinning", "地殼變薄"], ["shallow earthquakes", "淺源地震"], ["volcanoes", "火山"], ["GPS shows extension", "GPS 顯示拉張"]], answer: "divergent", label: ["Continental rifting", "大陸裂谷"],
      predict: ["elongated rift basins with lakes, high heat flow, thin crust, eventually a narrow sea", "狹長的裂谷盆地與湖泊、高地熱流、薄地殼，最終形成狹長海域"] },
    { id: "C", ev: [["many thrust faults", "大量逆衝斷層"], ["crustal shortening", "地殼縮短"], ["high mountains", "高山"], ["earthquakes", "地震"], ["very limited volcanoes", "火山極少"]], answer: "convergent", label: ["Continental collision", "大陸碰撞"],
      predict: ["a very thick crust, folded sedimentary rocks, metamorphic rocks uplifted, only shallow-to-intermediate earthquakes", "很厚的地殼、褶皺的沈積岩、抬升的變質岩、僅淺至中源地震"] },
    { id: "D", ev: [["shallow earthquakes", "淺源地震"], ["horizontally offset rivers", "被水平錯開的河流"], ["strike-slip faults", "走向滑移斷層"], ["few volcanoes", "火山很少"]], answer: "transform", label: ["Transform boundary", "錯動型邊界"],
      predict: ["a long linear fault valley, no trench, no deep earthquakes, GPS vectors parallel to the fault", "長直的斷層谷、沒有海溝、沒有深源地震、GPS 向量平行斷層"] }
  ];
  $("#region-grid").innerHTML = regions.map(r => `
    <article class="card region" data-id="${r.id}">
      <h3>Region ${r.id}</h3>
      <ul class="evidence">${r.ev.map(([en, zh]) => `<li>${en}<small>${zh}</small></li>`).join("")}</ul>
      <div class="choices">${Object.entries(boundaries).map(([k, b]) => `<button class="choice" data-pick="${k}"><b>${b.sym}</b>${bi(b.zh, b.en)}</button>`).join("")}</div>
      <div class="feedback"></div>
      <div class="predict-box">
        <p class="frame">If our model is correct, we should also observe ______.</p>
        <textarea name="predict-${r.id}" rows="2" placeholder="We predict … / 我們預測……"></textarea>
        <details class="answer"><summary>${bi("可能的預測", "Possible predictions")}</summary><p>${bi(r.predict[1], r.predict[0])}</p></details>
      </div>
    </article>`).join("");
  $$(".region").forEach(card => {
    const r = regions.find(x => x.id === card.dataset.id), fb = $(".feedback", card);
    const show = (pick) => {
      $$(".choice", card).forEach(c => { c.classList.remove("right", "wrong"); if (c.dataset.pick === pick) c.classList.add(pick === r.answer ? "right" : "wrong"); });
      if (pick === r.answer) {
        fb.className = "feedback ok";
        fb.innerHTML = `<b>${r.label[0]}</b> · ${r.label[1]}<br>${bi("接著回答：What mechanism explains it? What else do you predict?", "Now answer: What mechanism explains it? What else do you predict?")}`;
        store.set("region:" + r.id, true); checkRegions();
      } else { fb.className = "feedback no"; fb.innerHTML = bi("哪一條證據不符合？例如深源地震只會出現在隱沒帶。", "Which evidence does not fit? Deep earthquakes, for instance, occur only in subduction zones."); }
    };
    $$(".choice", card).forEach(c => c.addEventListener("click", () => show(c.dataset.pick)));
    if (store.get("region:" + r.id, false)) show(r.answer);
  });
  function checkRegions() {
    if (regions.every(r => store.get("region:" + r.id, false)) && !stamps.has("predict")) { stamps.add("predict"); store.set("stamps", [...stamps]); renderStamps(); toast("All regions ✓ 四個區域完成"); }
  }
  checkRegions();

  /* ---------------- CLIL frames + speech ---------------- */
  const frames = [
    ["Observation", "We observe that ______.", "我們觀察到……"],
    ["Claim", "We think this is a ______ boundary.", "我們認為這是……型板塊邊界。"],
    ["Evidence", "Our evidence is ______.", "我們的證據是……"],
    ["Explanation", "This can be explained by ______.", "這可以用……來解釋。"],
    ["Causal reasoning", "Because the plates are moving ______, the crust experiences ______.", "因為板塊……運動，地殼受到……"],
    ["Prediction", "If our model is correct, we should also observe ______.", "如果我們的模型正確，我們還應該觀察到……"],
    ["Model revision", "Based on the new evidence, we need to revise our model.", "根據新證據，我們需要修正模型。"]
  ];
  $("#frames-list").innerHTML = frames.map(([tag, en, zh]) => `<li><span class="fr-en" data-copy="${en}"><span class="fr-tag">${tag}</span>${en}<span class="fr-zh">${zh}</span></span><button class="say" data-say="${en.replace(/_+/g, "blank")}" title="Listen">🔊</button></li>`).join("");
  const canSpeak = "speechSynthesis" in window;
  function say(text) {
    if (!canSpeak) { toast("此瀏覽器不支援語音 · No speech support"); return; }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text); u.lang = "en-US"; u.rate = .92;
    const v = speechSynthesis.getVoices().find(v => /^en(-|_)/.test(v.lang) && /Google|Samantha|Daniel|Natural/i.test(v.name)) || speechSynthesis.getVoices().find(v => /^en/.test(v.lang));
    if (v) u.voice = v; speechSynthesis.speak(u);
  }
  document.addEventListener("click", e => {
    const s = e.target.closest("[data-say]"); if (s) { say(s.dataset.say); return; }
    const c = e.target.closest("[data-copy]"); if (c && navigator.clipboard) { navigator.clipboard.writeText(c.dataset.copy).then(() => toast("Copied 已複製")); }
  });

  /* ---------------- exit tickets ---------------- */
  const tickets = [
    { title: "Exit Ticket 1", zh: "第一節", qs: [
      ["Are earthquakes randomly distributed around the world?", "世界上的地震是否隨機分布？", "No. Earthquakes are concentrated in narrow belts. · 否，地震主要集中於特定帶狀區域。"],
      ["Normal faults + shallow earthquakes + a rift valley → most likely plate motion?", "正斷層＋淺源地震＋裂谷 → 最可能的板塊運動？", "Divergent boundary · 張裂型。"],
      ["Complete: We observe ______, so we infer ______.", "完成句子：We observe ______, so we infer ______.", "e.g. We observe normal faults and a rift valley, so we infer crustal extension."]] },
    { title: "Exit Ticket 2", zh: "第二節", qs: [
      ["East African Rift: normal faults, shallow earthquakes, volcanoes, long narrow basins. Write a CER.", "東非裂谷：正斷層、淺源地震、火山、狹長盆地。請完成 CER。", "Claim: the region is undergoing extension. Evidence: normal faults, shallow earthquakes, volcanoes, rift basins. Reasoning: when the crust is pulled apart, normal faults form and blocks move downward forming basins; mantle material rises and generates magma. · 地殼受到拉張時會形成正斷層；部分地塊下沉形成裂谷盆地，深部物質上升則可能產生岩漿。"]] },
    { title: "Final Exit Ticket", zh: "第三節", qs: [
      ["Complete: A scientific model is useful because ______.", "完成句子：A scientific model is useful because ______.", "A scientific model helps us explain observations and make predictions."],
      ["Deep earthquakes + trench + volcanic arc → most likely tectonic setting?", "深源地震＋海溝＋火山弧 → 最可能的構造環境？", "Subduction zone · 聚合型隱沒帶。"],
      ["If our model is correct, we should also observe ______.", "如果模型正確，我們還應該觀察到……", "e.g. reverse faults, compression, an inclined seismic zone. · 例如逆斷層、壓力、傾斜的地震帶。"]] }
  ];
  $("#ticket-grid").innerHTML = tickets.map((t, ti) => `
    <article class="card ticket"><h3>${t.title}<small> · ${t.zh}</small></h3>
      ${t.qs.map(([en, zh, ans], qi) => `<div class="q"><p>Q${qi + 1}. ${en}<small>${zh}</small></p><textarea name="ticket-${ti}-${qi}" rows="2"></textarea><details><summary>${bi("參考答案", "Reference answer")}</summary><p>${ans}</p></details></div>`).join("")}
    </article>`).join("");

  /* ---------------- AI form, export, clear ---------------- */
  bindPersist(document);
  $("#print-page").addEventListener("click", () => window.print());
  $("#clear-all").addEventListener("click", () => {
    if (!confirm("清除這台裝置上的所有紀錄？ Clear all saved work on this device?")) return;
    store.clear(); location.reload();
  });
  function exportPortfolio() {
    const f = new FormData($("#ai-form"));
    const v = k => (f.get(k) || "").toString().trim() || "—";
    const date = new Date().toISOString().slice(0, 10);
    const lines = [
      `# 板塊構造探究學習歷程 · Plate Tectonics Inquiry Portfolio`, ``, `日期 Date: ${date}`, ``,
      `## 1. 觀察 Observation`, ``, (store.get("field:observe-notes", "") || "—"), ``,
      `## 2. 神秘區域 Mysteries`, ``, ...mysteries.map(m => `- Mystery ${m.id}: ${store.get("mystery:" + m.id, false) ? "solved ✓" : "—"}`), ``,
      `## 3. 真實案例 CER`, ``,
      ...cases.flatMap(c => [`### ${c.en} · ${c.zh}`, `- **Claim**: ${store.get(`field:cer-${c.id}-claim`, "") || "—"}`, `- **Evidence**: ${store.get(`field:cer-${c.id}-evidence`, "") || "—"}`, `- **Reasoning**: ${store.get(`field:cer-${c.id}-reasoning`, "") || "—"}`, ``]),
      `## 4. Mystery Region 預測 Predictions`, ``, ...regions.map(r => `- Region ${r.id} (${store.get("region:" + r.id, false) ? "✓" : "—"}): ${store.get(`field:predict-${r.id}`, "") || "—"}`), ``,
      `## 5. AI 驗證與模型修正 AI check & revision`, ``,
      `- **Original model 原始模型**: ${v("original")}`, `- **Prompt**: ${v("prompt")}`, `- **AI response AI 回答**: ${v("response")}`, `- **Agree / disagree 同意／不同意**: ${v("agree")}`, `- **Evidence 證據**: ${v("evidence")}`, `- **Revised model 修正後模型**: ${v("revised")}`, `- **Reflection 反思**: ${v("reflection")}`, ``,
      `## 6. Exit tickets`, ``, ...tickets.flatMap((t, ti) => [`### ${t.title}`, ...t.qs.map((q, qi) => `- Q${qi + 1}: ${store.get(`field:ticket-${ti}-${qi}`, "") || "—"}`), ``]),
      `## 7. 探究護照 Inquiry passport`, ``, `${stamps.size} / ${total} stamps: ${[...stamps].join(", ") || "—"}`, ``
    ];
    const blob = new Blob([lines.join("\n")], { type: "text/markdown;charset=utf-8" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `plate-tectonics-portfolio-${date}.md`; a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000); toast("Exported 已匯出");
  }
  $$("[data-export]").forEach(b => b.addEventListener("click", exportPortfolio));

  /* ---------------- nav highlight ---------------- */
  const navLinks = $$(".topnav a");
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => { if (en.isIntersecting) navLinks.forEach(a => a.classList.toggle("current", a.getAttribute("href") === "#" + en.target.id)); });
  }, { rootMargin: "-40% 0px -55% 0px" });
  $$("main section[id]").forEach(s => io.observe(s));
})();
