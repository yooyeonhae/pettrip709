# ============================================================
# 펫트립 - 반려동물 동반 여행 가이드 (Streamlit 버전)
# 원본 React 프로젝트(src/)의 mock 데이터·판정 로직을 그대로 포팅했다.
# 실행: streamlit run app.py
# ============================================================

import base64
import math
import os
from io import BytesIO

import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="펫트립 - 반려동물 동반 여행 가이드", page_icon="🐾", layout="wide")

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def render_warm_theme():
    """앱 전체를 따뜻한 오렌지·크림 톤으로 물들이는 배경 CSS. 헤더/툴바도 투명하게 만들어 배경이 끊기지 않게 한다."""
    st.markdown(
        """
        <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
            background: linear-gradient(160deg, #fff6ec 0%, #ffe8d1 45%, #ffd3a1 100%);
        }
        [data-testid="stHeader"], [data-testid="stToolbar"] {
            background: transparent;
        }
        h1, h2, h3 { color: #b45309 !important; }
        .stButton button, div[data-testid="stButton"] button {
            background-color: #ff8c1a;
            color: #fff;
            border: none;
        }
        .stButton button:hover, div[data-testid="stButton"] button:hover {
            background-color: #f97316;
            color: #fff;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fff3e2 0%, #ffe0b8 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def _cutout_image_base64(filename, threshold=235, feather=25):
    """흰 배경을 투명하게 지워 그림 오브젝트만 남긴 PNG를 base64로 반환한다."""
    path = os.path.join(APP_DIR, filename)
    img = Image.open(path).convert("RGBA")
    pixels = img.getdata()
    new_pixels = []
    for r, g, b, a in pixels:
        brightness = (r + g + b) / 3
        if brightness >= threshold:
            new_pixels.append((r, g, b, 0))
        elif brightness >= threshold - feather:
            alpha = int(255 * (threshold - brightness) / feather)
            new_pixels.append((r, g, b, alpha))
        else:
            new_pixels.append((r, g, b, a))
    img.putdata(new_pixels)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def render_hero_image(filename, width_px=220):
    """상단 중앙에 배경을 지운 그림만 자연스럽게 배치한다 (틀·그림자 없음)."""
    b64 = _cutout_image_base64(filename)
    st.markdown(
        f"""
        <div style="text-align:center; margin: 0.2rem 0 0.6rem;">
            <img src="data:image/png;base64,{b64}" style="
                width:{width_px}px; max-width:55%; height:auto;
                filter: sepia(15%) saturate(140%) hue-rotate(-6deg) brightness(1.03);
            ">
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# 상수
# ------------------------------------------------------------
REGIONS = [
    {"code": "", "name": "전체"},
    {"code": "1", "name": "서울"},
    {"code": "6", "name": "부산"},
    {"code": "4", "name": "대구"},
    {"code": "2", "name": "인천"},
    {"code": "5", "name": "광주"},
    {"code": "3", "name": "대전"},
    {"code": "7", "name": "울산"},
    {"code": "8", "name": "세종"},
    {"code": "31", "name": "경기"},
    {"code": "32", "name": "강원"},
    {"code": "33", "name": "충북"},
    {"code": "34", "name": "충남"},
    {"code": "35", "name": "경북"},
    {"code": "36", "name": "경남"},
    {"code": "37", "name": "전북"},
    {"code": "38", "name": "전남"},
    {"code": "39", "name": "제주"},
]

PET_TYPES = [
    {"value": "dog", "label": "강아지", "emoji": "🐶"},
    {"value": "cat", "label": "고양이", "emoji": "🐱"},
    {"value": "etc", "label": "기타", "emoji": "🐾"},
]

PET_SIZES = [
    {"value": "small", "label": "소형", "desc": "~5kg"},
    {"value": "medium", "label": "중형", "desc": "5~15kg"},
    {"value": "large", "label": "대형", "desc": "15kg~"},
]

PET_ITEMS = [
    {"value": "carrier", "label": "이동장", "emoji": "🧳"},
    {"value": "leash", "label": "목줄", "emoji": "🦮"},
    {"value": "muzzle", "label": "입마개", "emoji": "😷"},
    {"value": "wasteBag", "label": "배변봉투", "emoji": "💩"},
]

CATEGORIES = [
    {"value": "cafe", "label": "카페/식당", "emoji": "☕"},
    {"value": "attraction", "label": "관광지", "emoji": "🏞️"},
    {"value": "lodging", "label": "숙소", "emoji": "🏨"},
    {"value": "park", "label": "공원/산책", "emoji": "🌳"},
    {"value": "culture", "label": "문화시설", "emoji": "🖼️"},
]

JUDGE_META = {
    "ok": {"label": "가능", "color": "#22c55e", "emoji": "🟢"},
    "warn": {"label": "조건부 가능", "color": "#eab308", "emoji": "🟡"},
    "no": {"label": "불가", "color": "#ef4444", "emoji": "🔴"},
}

NO_DATA_NOTICE = "정보 없음, 방문 전 재확인 권장"

# ------------------------------------------------------------
# API 키: 
# (키가 없으면 자동으로 mock 데이터로 동작한다)
# ------------------------------------------------------------
TOUR_API_KEY = "bcb9c56ce647784c28e44247f1ae7feabc585b174cc869951923a5b94932055a"   # 한국관광공사 TourAPI 4.0 서비스 키
KAKAO_MAP_KEY = ""  # 카카오맵 JS SDK 키

REGION_NAME_BY_CODE = {r["code"]: r["name"] for r in REGIONS}
TYPE_LABEL_BY_VALUE = {t["value"]: t["label"] for t in PET_TYPES}
SIZE_LABEL_BY_VALUE = {s["value"]: s["label"] for s in PET_SIZES}
ITEM_LABEL_BY_VALUE = {i["value"]: i["label"] for i in PET_ITEMS}
ITEM_EMOJI_BY_VALUE = {i["value"]: i["emoji"] for i in PET_ITEMS}
CATEGORY_LABEL_BY_VALUE = {c["value"]: f"{c['emoji']} {c['label']}" for c in CATEGORIES}

# ------------------------------------------------------------
# Mock 데이터 (API 키 없이 데모 가능)
# ------------------------------------------------------------
MOCK_PLACES = [
    {
        "id": "p1", "name": "멍냥카페 홍대점", "category": "cafe", "region": "1",
        "address": "서울특별시 마포구 양화로 12", "lat": 37.5563, "lng": 126.9236,
        "image": "https://picsum.photos/seed/petcafe1/600/400",
        "raw_rule": {
            "allowedAnimalsText": "소형견, 고양이 (대형견 불가)",
            "accompanyTypeText": "실내 동반 가능 (테이블 아래 대기)",
            "needMatterText": "이동장 또는 목줄 필수, 입마개는 맹견종만 해당",
            "furnishedItemsText": "반려동물 방석, 급수기 구비",
            "purchaseItemsText": "강아지 간식 판매",
            "rentalItemsText": "이동장 대여 불가",
            "accidentRiskText": "타 반려동물과의 접촉 시 주의, 목줄 필수",
            "extraFeeText": "반려동물 동반 시 테이블당 5,000원 추가",
        },
        "parsed_rule": {"allowedAnimals": ["dog", "cat"], "allowedSizes": ["small"], "maxWeight": 7, "requiredItems": ["leash"]},
    },
    {
        "id": "p2", "name": "해변산책 애견동반펜션", "category": "lodging", "region": "39",
        "address": "제주특별자치도 제주시 애월 해안로 20", "lat": 33.4625, "lng": 126.3252,
        "image": "https://picsum.photos/seed/petlodge1/600/400",
        "raw_rule": {
            "allowedAnimalsText": "반려견 전체 동반 가능 (종/크기 제한 없음)",
            "accompanyTypeText": "실내·실외 모두 동반 가능, 전용 마당 있음",
            "needMatterText": "배변봉투 필수 지참, 타 투숙객 배려 위해 목줄 권장",
            "furnishedItemsText": "반려동물 전용 침구, 식기 구비",
            "purchaseItemsText": "정보 없음",
            "rentalItemsText": "울타리 대여 가능(사전 문의)",
            "accidentRiskText": "마당 울타리 높이 낮음, 대형견 보호자 상시 동반 권장",
            "extraFeeText": "1마리당 20,000원 (2마리 이상 문의)",
        },
        "parsed_rule": {"allowedAnimals": ["dog"], "allowedSizes": ["small", "medium", "large"], "maxWeight": None, "requiredItems": ["wasteBag"]},
    },
    {
        "id": "p3", "name": "한옥마을 전통찻집", "category": "cafe", "region": "35",
        "address": "경상북도 경주시 교동 19", "lat": 35.8347, "lng": 129.2097,
        "image": "https://picsum.photos/seed/teahouse1/600/400",
        "raw_rule": {
            "allowedAnimalsText": "반려동물 동반 불가 (전통 가옥 특성상 실내 출입 제한)",
            "accompanyTypeText": "테라스석에 한해 소형견 이동장 동반만 가능",
            "needMatterText": "이동장 필수, 실내석 동반 불가",
            "furnishedItemsText": "정보 없음",
            "purchaseItemsText": "정보 없음",
            "rentalItemsText": "정보 없음",
            "accidentRiskText": "문화재 구역 인접, 소음/훼손 주의",
            "extraFeeText": "없음",
        },
        "parsed_rule": {"allowedAnimals": ["dog", "cat"], "allowedSizes": ["small"], "maxWeight": 5, "requiredItems": ["carrier"]},
    },
    {
        "id": "p4", "name": "강변 반려견 놀이터공원", "category": "park", "region": "31",
        "address": "경기도 가평군 청평면 강변로 100", "lat": 37.7333, "lng": 127.4235,
        "image": "https://picsum.photos/seed/dogpark1/600/400",
        "raw_rule": {
            "allowedAnimalsText": "반려견 전체 (품종 제한 없음, 예방접종 확인 필수)",
            "accompanyTypeText": "실외 자유방목 구역 있음",
            "needMatterText": "목줄 필수(자유방목장 제외), 배변봉투 필수, 예방접종 증명서 권장",
            "furnishedItemsText": "배변봉투함, 급수대 구비",
            "purchaseItemsText": "정보 없음",
            "rentalItemsText": "정보 없음",
            "accidentRiskText": "자유방목장 내 대형견-소형견 구역 분리, 입장 시 확인",
            "extraFeeText": "주차료 외 없음",
        },
        "parsed_rule": {"allowedAnimals": ["dog"], "allowedSizes": ["small", "medium", "large"], "maxWeight": None, "requiredItems": ["leash", "wasteBag"]},
    },
    {
        "id": "p5", "name": "오션뷰 루프탑 브런치", "category": "cafe", "region": "6",
        "address": "부산광역시 해운대구 달맞이길 62", "lat": 35.1587, "lng": 129.1604,
        "image": "https://picsum.photos/seed/rooftop1/600/400",
        "raw_rule": {
            "allowedAnimalsText": "소형/중형견, 고양이 (10kg 이하)",
            "accompanyTypeText": "루프탑 실외석 한정 동반 가능",
            "needMatterText": "이동장 필수, 입마개 권장(대형 품종 혼혈 시)",
            "furnishedItemsText": "반려동물 방석 구비",
            "purchaseItemsText": "반려동물 전용 간식 판매",
            "rentalItemsText": "정보 없음",
            "accidentRiskText": "루프탑 난간 근접 구역 보호자 주의",
            "extraFeeText": "없음",
        },
        "parsed_rule": {"allowedAnimals": ["dog", "cat"], "allowedSizes": ["small", "medium"], "maxWeight": 10, "requiredItems": ["carrier"]},
    },
    {
        "id": "p6", "name": "설악산 국립공원 탐방로", "category": "attraction", "region": "32",
        "address": "강원도 속초시 설악산로 833", "lat": 38.1667, "lng": 128.4654,
        "image": "https://picsum.photos/seed/mountain1/600/400",
        "raw_rule": {
            "allowedAnimalsText": "반려동물 동반 불가 (국립공원 생태보호구역)",
            "accompanyTypeText": "동반 불가",
            "needMatterText": "해당 없음",
            "furnishedItemsText": "해당 없음",
            "purchaseItemsText": "해당 없음",
            "rentalItemsText": "해당 없음",
            "accidentRiskText": "야생동물 서식지, 반려동물 출입 시 생태계 교란 우려",
            "extraFeeText": "해당 없음",
        },
        "parsed_rule": {"allowedAnimals": [], "allowedSizes": [], "maxWeight": 0, "requiredItems": []},
    },
    {
        "id": "p7", "name": "반려동물 동반 미술관", "category": "culture", "region": "1",
        "address": "서울특별시 종로구 자하문로 4", "lat": 37.5826, "lng": 126.9736,
        "image": "https://picsum.photos/seed/gallery1/600/400",
        "raw_rule": {
            "allowedAnimalsText": "소형견, 고양이, 기타 소동물 (전시장 특성상 15kg 이하)",
            "accompanyTypeText": "이동장 상시 착용 시에만 실내 동반 가능",
            "needMatterText": "이동장 필수, 목줄 필수(이동 중), 소음 자제",
            "furnishedItemsText": "정보 없음",
            "purchaseItemsText": "정보 없음",
            "rentalItemsText": "이동장 유료 대여 가능",
            "accidentRiskText": "전시품 훼손 방지를 위해 보호자가 이동장에서 꺼내지 않아야 함",
            "extraFeeText": "반려동물 입장료 3,000원",
        },
        "parsed_rule": {"allowedAnimals": ["dog", "cat", "etc"], "allowedSizes": ["small", "medium"], "maxWeight": 15, "requiredItems": ["carrier", "leash"]},
    },
    {
        "id": "p8", "name": "남해 반려동물 동반 캠핑장", "category": "lodging", "region": "36",
        "address": "경상남도 남해군 남면 해안도로 55", "lat": 34.7833, "lng": 127.8926,
        "image": "https://picsum.photos/seed/camping1/600/400",
        "raw_rule": {
            "allowedAnimalsText": "반려견/반려묘 동반 가능 (사이트별 상이, 사전 확인 요망)",
            "accompanyTypeText": "개별 사이트 실외 동반, 화장실/샤워장 동반 불가",
            "needMatterText": "목줄 필수, 입마개(맹견 5종), 배변봉투 필수",
            "furnishedItemsText": "정보 없음",
            "purchaseItemsText": "정보 없음",
            "rentalItemsText": "정보 없음",
            "accidentRiskText": "인근 사이트와 거리두기 권장, 야간 소음 주의",
            "extraFeeText": "1마리 10,000원",
        },
        "parsed_rule": {"allowedAnimals": ["dog", "cat"], "allowedSizes": ["small", "medium", "large"], "maxWeight": None, "requiredItems": ["leash", "wasteBag"]},
    },
]

for _p in MOCK_PLACES:
    _p["region_name"] = REGION_NAME_BY_CODE.get(_p["region"], "")


# ------------------------------------------------------------
# 판정 로직 (원본 src/lib/judgeEntry.js 포팅)
# ------------------------------------------------------------
def judge_entry(pet, rule):
    """반려동물 프로필과 장소의 동반 규정(parsed_rule)을 대조해 가능/조건부 가능/불가로 판정한다."""
    if not rule:
        return {"level": "warn", "reason": NO_DATA_NOTICE, "missing_items": [], "no_data": True}

    allowed_animals = rule.get("allowedAnimals") or []
    allowed_sizes = rule.get("allowedSizes") or []
    max_weight = rule.get("maxWeight")
    required_items = rule.get("requiredItems") or []

    # 1. 동물 종류
    if pet["type"] not in allowed_animals:
        return {
            "level": "no",
            "reason": f"이 장소는 {TYPE_LABEL_BY_VALUE.get(pet['type'], pet['type'])} 동반이 불가능해요.",
            "missing_items": [],
        }

    # 2. 무게
    weight = pet.get("weight")
    if max_weight is not None and weight is not None and weight > max_weight:
        return {
            "level": "no",
            "reason": f"무게 제한 {max_weight}kg를 초과해요. (우리 아이 {weight}kg)",
            "missing_items": [],
        }

    # 3. 크기
    if allowed_sizes and pet["size"] not in allowed_sizes:
        allowed_label = ", ".join(SIZE_LABEL_BY_VALUE.get(s, s) for s in allowed_sizes)
        return {
            "level": "no",
            "reason": f"{SIZE_LABEL_BY_VALUE.get(pet['size'], pet['size'])} 사이즈는 동반이 어려워요. (허용: {allowed_label})",
            "missing_items": [],
        }

    # 4. 준비물 (보완 가능한 조건 -> 조건부 가능)
    missing_items = [i for i in required_items if i not in (pet.get("items") or [])]
    if missing_items:
        return {
            "level": "warn",
            "reason": f"필요 준비물: {', '.join(ITEM_LABEL_BY_VALUE.get(i, i) for i in missing_items)}",
            "missing_items": missing_items,
        }

    return {"level": "ok", "reason": "모든 조건을 충족했어요!", "missing_items": []}


def build_interpretation(pet, rule, judgement):
    """모호한 규정 원문을 우리 아이 프로필 기준으로 사람 친화적인 문장으로 번역한다."""
    breed_or_type = pet.get("breed") or TYPE_LABEL_BY_VALUE.get(pet["type"], pet["type"])
    pet_desc = f"{breed_or_type} {pet['weight']}kg".strip() if pet.get("weight") else breed_or_type

    if judgement.get("no_data"):
        return f"이 장소의 반려동물 동반 규정 정보가 아직 등록되어 있지 않아요. {judgement['reason']}"

    if judgement["level"] == "no":
        return f"우리 아이({pet_desc})는 {judgement['reason']}"

    if judgement["level"] == "warn":
        conditions = []
        if rule and rule.get("allowedSizes"):
            conditions.append(f"{'·'.join(SIZE_LABEL_BY_VALUE.get(s, s) for s in rule['allowedSizes'])} 사이즈")
        if rule and rule.get("maxWeight") is not None:
            conditions.append(f"{rule['maxWeight']}kg 이하")
        condition_text = f"{', '.join(conditions)} 조건 충족! " if conditions else ""
        missing_text = ", ".join(ITEM_LABEL_BY_VALUE.get(i, i) for i in judgement["missing_items"])
        return f"우리 아이({pet_desc})는 {condition_text}단, {missing_text}이(가) 필요해요."

    return f"우리 아이({pet_desc})는 이 장소의 모든 동반 조건을 충족해서 바로 입장할 수 있어요!"


def distance_km(a, b, c, d):
    R = 6371
    d_lat = math.radians(c - a)
    d_lng = math.radians(d - b)
    s = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(a)) * math.cos(math.radians(c)) * math.sin(d_lng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(s), math.sqrt(1 - s))


# ------------------------------------------------------------
# 세션 상태 초기화
# ------------------------------------------------------------
if "pet_profile" not in st.session_state:
    st.session_state.pet_profile = {
        "name": "", "type": "", "breed": "", "weight": None, "size": "", "items": [], "vaccinated": False,
    }
if "favorites" not in st.session_state:
    st.session_state.favorites = {}  # id -> place


def toggle_favorite(place):
    favs = st.session_state.favorites
    if place["id"] in favs:
        del favs[place["id"]]
    else:
        favs[place["id"]] = place


# ------------------------------------------------------------
# 사이드바: 우리 아이 프로필
# ------------------------------------------------------------
with st.sidebar:
    st.header("🐾 우리 아이 프로필")
    st.caption("프로필을 등록하면 장소마다 우리 아이 기준 맞춤 판정을 보여드려요.")

    profile = st.session_state.pet_profile
    profile["name"] = st.text_input("이름 (선택)", value=profile["name"])

    type_options = [t["value"] for t in PET_TYPES]
    type_index = type_options.index(profile["type"]) if profile["type"] in type_options else 0
    profile["type"] = st.radio(
        "종류", type_options, index=type_index,
        format_func=lambda v: f"{next(t['emoji'] for t in PET_TYPES if t['value'] == v)} {TYPE_LABEL_BY_VALUE[v]}",
        horizontal=True,
    )

    profile["breed"] = st.text_input("품종 (선택)", value=profile["breed"], placeholder="예: 포메라니안")
    profile["weight"] = st.number_input("몸무게 (kg)", min_value=0.0, max_value=100.0, step=0.5, value=float(profile["weight"] or 0))

    size_options = [s["value"] for s in PET_SIZES]
    size_index = size_options.index(profile["size"]) if profile["size"] in size_options else 0
    profile["size"] = st.selectbox(
        "크기", size_options, index=size_index,
        format_func=lambda v: f"{SIZE_LABEL_BY_VALUE[v]} ({next(s['desc'] for s in PET_SIZES if s['value'] == v)})",
    )

    profile["items"] = st.multiselect(
        "보유 준비물", [i["value"] for i in PET_ITEMS], default=profile["items"],
        format_func=lambda v: f"{ITEM_EMOJI_BY_VALUE[v]} {ITEM_LABEL_BY_VALUE[v]}",
    )
    profile["vaccinated"] = st.checkbox("예방접종 완료", value=profile["vaccinated"])

    profile_ready = bool(profile["type"] and profile["size"])
    if not profile_ready:
        st.info("종류·크기를 선택하면 맞춤 판정이 활성화돼요.")


# ------------------------------------------------------------
# 메인 화면
# ------------------------------------------------------------
render_warm_theme()
render_hero_image("여행가는 반려동물.png")

st.title("🐾 펫트립")
st.caption("반려동물과 함께 갈 수 있는 여행지를 찾아보세요")

tab_browse, tab_favorites = st.tabs(["🔍 둘러보기", f"❤️ 찜한 여행지 ({len(st.session_state.favorites)})"])


def render_place_card(place, pet_profile, profile_ready):
    with st.container(border=True):
        cols = st.columns([1, 3])
        with cols[0]:
            st.image(place["image"], width="stretch")
        with cols[1]:
            header_col, fav_col = st.columns([5, 1])
            with header_col:
                st.subheader(f"{place['name']}")
                st.caption(f"{CATEGORY_LABEL_BY_VALUE.get(place['category'], place['category'])} · {place['region_name']} · {place['address']}")
            with fav_col:
                is_fav = place["id"] in st.session_state.favorites
                if st.button("💔 해제" if is_fav else "🤍 찜", key=f"fav_{place['id']}"):
                    toggle_favorite(place)
                    st.rerun()

            if profile_ready:
                judgement = judge_entry(pet_profile, place["parsed_rule"])
                meta = JUDGE_META[judgement["level"]]
                st.markdown(
                    f"<span style='color:{meta['color']}; font-weight:600;'>{meta['emoji']} {meta['label']}</span>",
                    unsafe_allow_html=True,
                )
                st.write(build_interpretation(pet_profile, place["parsed_rule"], judgement))
            else:
                st.info("사이드바에서 프로필을 등록하면 맞춤 판정을 볼 수 있어요.")

            with st.expander("조건 원문 보기"):
                for label, key in [
                    ("동반 가능 동물", "allowedAnimalsText"),
                    ("동반 유형", "accompanyTypeText"),
                    ("동반 시 필요사항", "needMatterText"),
                    ("구비 물품", "furnishedItemsText"),
                    ("구매 물품", "purchaseItemsText"),
                    ("렌탈 물품", "rentalItemsText"),
                    ("사고대비 사항", "accidentRiskText"),
                    ("추가 요금", "extraFeeText"),
                ]:
                    st.markdown(f"**{label}**: {place['raw_rule'].get(key, NO_DATA_NOTICE)}")


with tab_browse:
    filter_cols = st.columns([2, 3, 3])
    with filter_cols[0]:
        region_code = st.selectbox(
            "지역", [r["code"] for r in REGIONS],
            format_func=lambda c: REGION_NAME_BY_CODE.get(c, "전체"),
        )
    with filter_cols[1]:
        category_values = st.multiselect(
            "카테고리", [c["value"] for c in CATEGORIES],
            format_func=lambda v: CATEGORY_LABEL_BY_VALUE.get(v, v),
        )
    with filter_cols[2]:
        keyword = st.text_input("검색어", placeholder="장소명 또는 주소로 검색")

    filtered = [
        p for p in MOCK_PLACES
        if (not region_code or p["region"] == region_code)
        and (not category_values or p["category"] in category_values)
        and (not keyword.strip() or keyword.strip().lower() in p["name"].lower() or keyword.strip().lower() in p["address"].lower())
    ]

    st.write(f"총 **{len(filtered)}곳**의 여행지를 찾았어요.")

    if filtered:
        map_df = pd.DataFrame([{"lat": p["lat"], "lon": p["lng"]} for p in filtered])
        st.map(map_df, size=60)

    profile_ready = bool(profile["type"] and profile["size"])
    for place in filtered:
        render_place_card(place, profile, profile_ready)

    if not filtered:
        st.warning("조건에 맞는 여행지가 없어요. 필터를 조정해보세요.")

with tab_favorites:
    favorites = list(st.session_state.favorites.values())
    if not favorites:
        st.info("아직 찜한 여행지가 없어요. 둘러보기 탭에서 마음에 드는 곳을 찜해보세요!")
    else:
        profile_ready = bool(profile["type"] and profile["size"])
        for place in favorites:
            render_place_card(place, profile, profile_ready)

st.divider()
st.caption("데이터 출처: 한국관광공사 TourAPI 4.0 (KorService2 · KorPetTourService), 공공데이터포털 (data.go.kr) · 현재 화면은 데모용 mock 데이터입니다.")
