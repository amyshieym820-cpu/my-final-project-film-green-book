import math
import urllib.parse
import requests
import streamlit as st
from factors import (
    CAT_FACTORS,
    METHOD_FACTORS,
    MODE_FACTORS,
    TRUCK_FACTOR,
    ROAD_MULTIPLIER,
    MEAL_CO2E,
    DRINK_WATER_L,
    TREE_CO2E_YEAR,
    THRESHOLD_MID,
    THRESHOLD_HIGH,
    NO_REUSE_CATS,
)

st.set_page_config(
    page_title="Film Green Book · Art Department Carbon Calculator",
    page_icon="🌿",
    layout="wide",
)

# Custom subtle styling matching the #0E3B2C theme
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #0E3B2C;
        color: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 16px;
    }
    .metric-big {
        font-size: 3.2rem;
        font-weight: 700;
        line-height: 1.05;
        margin: 8px 0 14px 0;
    }
    .metric-sub {
        display: flex;
        justify-content: space-between;
        border-top: 1px solid rgba(255,255,255,0.25);
        padding: 8px 0;
        font-size: 0.9rem;
    }
    .save-box {
        background-color: #F2F5F4;
        border-radius: 14px;
        padding: 18px;
        margin-top: 12px;
    }
    .sug-box {
        border: 1px solid #D1DBD7;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .badge-save {
        background-color: #E2EAE7;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def haversine(lat1, lon1, lat2, lon2):
    r = math.radians
    dl = r(lat2 - lat1)
    dn = r(lon2 - lon1)
    h = math.sin(dl / 2) ** 2 + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(dn / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def geocode_address(query, kakao_key=""):
    q = query.strip()
    if not q:
        return None
    # 1. Try Kakao Local API if REST API key is provided
    if kakao_key:
        headers = {"Authorization": f"KakaoAK {kakao_key}"}
        try:
            res = requests.get(
                "https://dapi.kakao.com/v2/local/search/keyword.json",
                headers=headers,
                params={"query": q, "size": 1},
                timeout=4,
            ).json()
            if res.get("documents"):
                doc = res["documents"][0]
                return (float(doc["y"]), float(doc["x"]))
            res2 = requests.get(
                "https://dapi.kakao.com/v2/local/search/address.json",
                headers=headers,
                params={"query": q, "size": 1},
                timeout=4,
            ).json()
            if res2.get("documents"):
                doc = res2["documents"][0]
                return (float(doc["y"]), float(doc["x"]))
        except Exception:
            pass

    # 2. Fallback to OpenStreetMap Nominatim
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"format": "jsonv2", "limit": 1, "countrycodes": "kr", "q": q},
            headers={"User-Agent": "FilmGreenBook/1.0"},
            timeout=5,
        ).json()
        if res:
            return (float(res[0]["lat"]), float(res[0]["lon"]))
    except Exception:
        pass
    return None


def get_road_distance_km(coord1, coord2):
    if not coord1 or not coord2:
        return None, ""
    try:
        url = f"https://router.project-osrm.org/route/v1/driving/{coord1[1]},{coord1[0]};{coord2[1]},{coord2[0]}?overview=false"
        res = requests.get(url, timeout=4).json()
        if res.get("routes"):
            km = round(res["routes"][0]["distance"] / 100) / 10
            return km, "Road distance by OSRM"
    except Exception:
        pass
    km = round(haversine(coord1[0], coord1[1], coord2[0], coord2[1]) * ROAD_MULTIPLIER * 10) / 10
    return km, f"Estimated from straight-line distance × {ROAD_MULTIPLIER}"


def calc_item(item, ov_method=None, ov_ship=None, ov_b=None):
    m_key = ov_method or item["method"]
    _, is_online, mult, pk = METHOD_FACTORS[m_key]
    prod_factor, water_factor = CAT_FACTORS[item["cat"]]
    total_w = item["w"] * item["q"]
    km = item["km"]

    prod = total_w * prod_factor * mult
    if is_online:
        ship = ov_ship or item["ship"]
        b = max(1, ov_b if ov_b is not None else item["b"]) if ship == "bundle" else 1
        tr = math.ceil(item["q"] / b) * pk + total_w * km * TRUCK_FACTOR
    else:
        _, mode_factor = MODE_FACTORS[item["mode"]]
        tr = km * 2 * mode_factor + (total_w * 150 * TRUCK_FACTOR if m_key == "daiso" else 0.0)

    water = total_w * water_factor * (1.0 - mult)
    return {"prod": prod, "tr": tr, "total": prod + tr, "water": water}


def method_label(m_key, ship="single"):
    name, is_online, _, _ = METHOD_FACTORS[m_key]
    if is_online:
        return f"{name} ({'bundled' if ship == 'bundle' else 'shipped individually'})"
    return name


def new_item():
    return {
        "name": "",
        "cat": "Wood / plywood",
        "w": 1.0,
        "q": 1,
        "method": "coupang",
        "ship": "single",
        "b": 1,
        "mode": "transit",
        "o": "",
        "d": "",
        "km": 0.0,
        "hint": "",
    }


if "items" not in st.session_state:
    st.session_state.items = [new_item()]

# Header
st.title("Film Green Book")
st.write(
    "See how much carbon your art department saves depending on where and how you source props and materials. "
    "Add an item, pick a purchase method and route, and get the savings and alternatives right away."
)

with st.expander("Address search settings (Optional Kakao REST API Key)"):
    kakao_key = st.text_input(
        "Kakao REST API Key (leave empty to use OpenStreetMap)",
        type="password",
        placeholder="Paste your Kakao REST API key here",
    )
    st.caption(
        "Without a key, distance calculation uses OpenStreetMap Nominatim + OSRM road routing. "
        "You can also enter one-way distance (km) directly."
    )

col_left, col_right = st.columns([1.5, 1.0], gap="large")

with col_left:
    st.subheader("Props and materials")

    if not st.session_state.items:
        st.info("No items yet. Click 'Add an item' below to start calculating.")

    remove_idx = None
    for idx, it in enumerate(st.session_state.items):
        with st.container(border=True):
            r1c1, r1c2 = st.columns(2)
            it["name"] = r1c1.text_input(
                "Item name", value=it["name"], placeholder="e.g. Set plywood", key=f"name_{idx}"
            )
            cat_keys = list(CAT_FACTORS.keys())
            it["cat"] = r1c2.selectbox(
                "Material",
                cat_keys,
                index=cat_keys.index(it["cat"]),
                key=f"cat_{idx}",
            )

            r2c1, r2c2, r2c3 = st.columns(3)
            it["w"] = r2c1.number_input(
                "Weight each (kg)", min_value=0.0, step=0.1, value=float(it["w"]), key=f"w_{idx}"
            )
            it["q"] = r2c2.number_input(
                "Quantity", min_value=1, step=1, value=int(it["q"]), key=f"q_{idx}"
            )
            method_keys = list(METHOD_FACTORS.keys())
            it["method"] = r2c3.selectbox(
                "Purchase method",
                method_keys,
                index=method_keys.index(it["method"]),
                format_func=lambda k: METHOD_FACTORS[k][0],
                key=f"method_{idx}",
            )

            _, is_online, _, _ = METHOD_FACTORS[it["method"]]
            if is_online:
                r3c1, r3c2 = st.columns(2)
                it["ship"] = r3c1.selectbox(
                    "Shipping",
                    ["single", "bundle"],
                    index=0 if it["ship"] == "single" else 1,
                    format_func=lambda s: "Individual" if s == "single" else "Bundled",
                    key=f"ship_{idx}",
                )
                it["b"] = r3c2.number_input(
                    "Items per box",
                    min_value=1,
                    step=1,
                    value=max(1, int(it["b"])),
                    disabled=(it["ship"] != "bundle"),
                    key=f"b_{idx}",
                )
            else:
                mode_keys = list(MODE_FACTORS.keys())
                it["mode"] = st.selectbox(
                    "Travel mode (round trip)",
                    mode_keys,
                    index=mode_keys.index(it["mode"]),
                    format_func=lambda k: MODE_FACTORS[k][0],
                    key=f"mode_{idx}",
                )

            r4c1, r4c2 = st.columns(2)
            it["o"] = r4c1.text_input(
                "Origin (seller / warehouse)",
                value=it["o"],
                placeholder="e.g. 서울 성동구 성수이로",
                key=f"o_{idx}",
            )
            it["d"] = r4c2.text_input(
                "Destination (set / workshop)",
                value=it["d"],
                placeholder="e.g. 경기 파주시 탄현면",
                key=f"d_{idx}",
            )

            r5c1, r5c2, r5c3 = st.columns([1.2, 1.2, 1.0])
            if r5c1.button("Calculate Route Distance", key=f"calc_dist_{idx}"):
                with st.spinner("Locating addresses..."):
                    c1 = geocode_address(it["o"], kakao_key)
                    c2 = geocode_address(it["d"], kakao_key)
                    if c1 and c2:
                        km, hint = get_road_distance_km(c1, c2)
                        it["km"] = km
                        it["hint"] = hint
                    else:
                        it["hint"] = "Could not locate one or both addresses. Enter distance manually."

            it["km"] = r5c2.number_input(
                "Distance (km, one way)",
                min_value=0.0,
                step=0.1,
                value=float(it["km"]),
                key=f"km_{idx}",
            )
            gmaps_url = (
                "https://www.google.com/maps/dir/?api=1&origin="
                + urllib.parse.quote(it["o"])
                + "&destination="
                + urllib.parse.quote(it["d"])
            )
            r5c3.markdown(f"<br>[Open in Google Maps]({gmaps_url})")

            if it["hint"]:
                st.caption(it["hint"])

            c_res = calc_item(it)
            f1, f2 = st.columns([3, 1])
            f1.markdown(
                f"**{c_res['total']:.1f} kg CO₂e** (production {c_res['prod']:.1f} + transport {c_res['tr']:.1f})"
            )
            if f2.button("Remove", key=f"del_{idx}"):
                remove_idx = idx

    if remove_idx is not None:
        st.session_state.items.pop(remove_idx)
        st.rerun()

    if st.button("➕ Add an item", type="primary", use_container_width=True):
        st.session_state.items.append(new_item())
        st.rerun()

# Calculations for Right Panel
total_co2 = 0.0
base_co2 = 0.0
prod_co2 = 0.0
trans_co2 = 0.0
water_saved = 0.0
item_results = []

for it in st.session_state.items:
    c = calc_item(it)
    b = calc_item(it, ov_method="coupang", ov_ship="single")
    total_co2 += c["total"]
    base_co2 += b["total"]
    prod_co2 += c["prod"]
    trans_co2 += c["tr"]
    water_saved += c["water"]
    item_results.append((it, c))

with col_right:
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size:0.9rem; opacity:0.85;">Total carbon emissions for all purchases</div>
            <div class="metric-big">{total_co2:,.1f} <span style="font-size:1.1rem; font-weight:500;">kg CO₂e</span></div>
            <div class="metric-sub"><span>If every item were bought new on Coupang (single)</span><b>{base_co2:,.1f} kg</b></div>
            <div class="metric-sub"><span>Production</span><b>{prod_co2:,.1f} kg</b></div>
            <div class="metric-sub"><span>Packaging, transport, and travel</span><b>{trans_co2:,.1f} kg</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if total_co2 >= THRESHOLD_HIGH:
        st.error("High emissions. Check the alternatives below.")
    elif total_co2 >= THRESHOLD_MID:
        st.warning("Moderate emissions. See if any items can be reduced.")
    else:
        st.success("Low emissions.")

    saved_co2 = max(0.0, base_co2 - total_co2)
    pct = (saved_co2 / base_co2 * 100) if base_co2 > 0 else 0.0
    meals = saved_co2 / MEAL_CO2E
    people_meals = meals / 3.0
    people_water = round(water_saved / DRINK_WATER_L)
    trees = saved_co2 / TREE_CO2E_YEAR

    st.markdown(
        f"""
        <div class="save-box">
            <h4 style="margin:0 0 8px 0;">Saved by your sourcing choices</h4>
            <ul style="margin:0; padding-left:18px;">
                <li><b>{saved_co2:,.1f} kg</b> of carbon avoided ({pct:.1f}%)</li>
                <li>About <b>{meals:,.1f} meals</b> of carbon footprint, or <b>{people_meals:,.1f} people</b> eating three meals a day for a day</li>
                <li><b>{round(water_saved):,} L</b> of water footprint avoided, enough drinking water for <b>{people_water:,} people</b> for a day</li>
                <li>The yearly CO₂ absorption of <b>{trees:,.1f} trees</b></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# Alternatives & Reduction Tips
suggestions = []
for it, c in item_results:
    best = None
    for m_key, (_, is_on, _, _) in METHOD_FACTORS.items():
        if it["cat"] in NO_REUSE_CATS and m_key in ("danggeun", "rental", "reuse"):
            continue
        if m_key == it["method"] and not (is_on and it["ship"] == "single"):
            continue
        alt = calc_item(
            it,
            ov_method=m_key,
            ov_ship="bundle" if is_on else None,
            ov_b=it["q"] if is_on else None,
        )
        if best is None or alt["total"] < best["alt"]["total"]:
            best = {"m_key": m_key, "alt": alt, "ship": "bundle" if is_on else "single"}

    if best:
        diff = c["total"] - best["alt"]["total"]
        if diff >= 0.3 and (diff / max(c["total"], 1e-6)) >= 0.1:
            suggestions.append({"it": it, "c": c, "best": best, "diff": diff})

suggestions.sort(key=lambda x: x["diff"], reverse=True)

if suggestions:
    extra_save = sum(s["diff"] for s in suggestions)
    extra_pct = extra_save / max(total_co2, 0.01) * 100
    st.subheader("Ways to cut emissions")
    st.caption(
        f"Applying every alternative below could save another **{extra_save:,.1f} kg** ({extra_pct:.1f}%). "
        "Check stock, quality, and schedule before switching."
    )
    for s in suggestions:
        title = s["it"]["name"] or "Untitled item"
        curr_lbl = method_label(s["it"]["method"], s["it"]["ship"])
        best_lbl = method_label(s["best"]["m_key"], s["best"]["ship"])
        st.markdown(
            f"""
            <div class="sug-box">
                <b>{title}</b><br>
                {curr_lbl}: {s['c']['total']:.1f} kg → <b>{best_lbl}</b>: {s['best']['alt']['total']:.1f} kg
                <span class="badge-save">−{s['diff']:.1f} kg</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.subheader("How to reduce carbon")
st.markdown(
    """
- **Reuse first.** Reusing stock, scrap, or rental props cuts nearly all production emissions, which are the largest share for most items.
- **Buy used (Danggeun).** Used furniture, fabric, and fixtures avoid new production. Pick up in one trip.
- **Bundle online orders.** On Coupang and Naver, combine items into fewer boxes instead of shipping each one separately.
- **Cut trips and distance.** Combine store pickups, source close to the set, and use public transit or a shared van instead of a car.
- **Choose lower-carbon materials.** Fabric and electronics have the highest footprint per kg. Wood, paper, and glass are much lower.
- **Buy only what you need.** Rent for one-day items, avoid spares, and plan quantities with the shooting schedule.
- **Plan the afterlife.** After wrap, store or donate props and scrap so the next production can reuse them.
"""
)
