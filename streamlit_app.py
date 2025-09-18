import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import requests
from io import StringIO

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="물러서는 땅, 다가오는 바다",
    page_icon="🌊",
    layout="wide"
)

# --- 커스텀 스타일 적용 (화이트 테마) ---
st.markdown("""
<style>
/* Streamlit 앱의 메인 배경 및 폰트 */
.stApp {
    background-color: #ffffff; /* 흰색 배경 */
    color: #333333; /* 기본 텍스트 색상 */
    font-family: 'Noto Sans KR', sans-serif;
}

/* 헤더와 제목 스타일 */
h1 {
    font-size: 2.8rem;
    color: #0d3d56; /* 깊은 파란색 */
    text-align: center;
    text-shadow: 1px 1px 2px #cccccc;
}
h2 {
    font-size: 2rem;
    color: #0072b2; /* 중간 파란색 */
    border-bottom: 2px solid #0072b2;
    padding-bottom: 10px;
    margin-top: 40px;
}
h3 {
    font-size: 1.5rem;
    color: #0d3d56;
    margin-top: 30px;
}

/* 본문 텍스트 스타일 */
p, li {
    font-size: 1.1rem;
    line-height: 1.8;
}

/* 인용구 또는 강조 블록 스타일 */
.report-quote {
    background-color: #e6f7ff; /* 밝은 하늘색 배경 */
    border-left: 5px solid #0072b2;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
    font-style: italic;
    color: #333333;
}

/* 사이드바 스타일 */
.st-emotion-cache-16txtl3 {
    background-color: #f0f5f9; /* 밝은 회색 배경 */
}

/* expander 스타일 */
.st-emotion-cache-p5msec {
    border: 1px solid #d0d0d0;
}

</style>
""", unsafe_allow_html=True)


# --- 사이드바 ---
st.sidebar.header("🗺️ 사례 연구")
st.sidebar.subheader("투발루의 현실")
st.sidebar.image("https://img.hani.co.kr/imgdb/original/2021/1109/20211109502389.jpg",
             caption="물에 잠긴 국토에서 연설하는 투발루 외교장관 (2021)")
st.sidebar.info("""
투발루는 평균 해발고도가 2~3m에 불과하여 해수면 상승에 가장 큰 위협을 받고 있습니다. 바닷물 유입으로 농경지와 식수원이 오염되고, 주민들은 '환경 난민'이 되어 이주를 고민하고 있습니다.
""")


# --- 메인 대시보드 ---
st.markdown("<h1>물러서는 땅, 다가오는 바다</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555555;'>해수면 상승 인터랙티브 대시보드</h3>", unsafe_allow_html=True)
st.divider()

# --- 서론 ---
st.header("서론: 우리 눈앞에 닥친 현실")
st.markdown("""
<p class="report-quote">
인류의 기술이 나날이 발전함과 동시에 세상은 황폐해져 가고 있습니다.<br>
기온은 해마다 오르고, 북극과 남극의 빙하는 녹아내리며, 남극에서는 아름다운 꽃을 볼 수 있게 되었습니다. 바다는 따뜻해지고 해수면은 조용히 그러나 확실하게 높아지고 있습니다.
</p>
""", unsafe_allow_html=True)
st.write("지금 이 순간에도 우리 삶의 터전은 서서히 잠식당하고 있는 것입니다. 이 대시보드는 해수면 상승의 심각성을 데이터로 직접 확인하고, 미래의 위험을 시뮬레이션하며, 우리가 나아가야 할 길을 함께 고민하고자 합니다.")
st.divider()


# --- 데이터 시각화 섹션 (고정 데이터 사용) ---
st.header("1. 과거와 현재: 해수면 상승 데이터 분석")

def build_estimated_gmsl():
    years = np.arange(1900, 2026)
    gmsl_mm = np.zeros_like(years, dtype=float)
    for i, y in enumerate(years):
        if y <= 1992: gmsl_mm[i] = (y - 1900) * 1.75
        else: gmsl_mm[i] = (1992 - 1900) * 1.75 + (y - 1992) * 3.4
    return pd.DataFrame({"year": years, "gmsl_mm": gmsl_mm})

df = build_estimated_gmsl()

st.subheader("지구 평균 해수면 변화 (1900-2025 추정치)")
df_plot = df.copy()
df_plot = df_plot[(df_plot['year'] >= 1900) & (df_plot['year'] <= 2025)].sort_values('year')
df_plot['gmsl_mm'] -= df_plot['gmsl_mm'].iloc[0]

st.line_chart(df_plot.rename(columns={'year':'index'}).set_index('index')['gmsl_mm'], color="#ff4b4b")

latest_year = int(df_plot['year'].max())
latest_val = float(df_plot.iloc[-1]['gmsl_mm'])
st.metric(label=f"{latest_year}년 기준 상대 해수면 상승 (추정)", value=f"{latest_val:.1f} mm")
st.caption("그래프: 1900년 대비 지구 평균 해수면 높이 변화(mm). 교육 및 설명 목적의 추정치입니다.")
st.divider()


# --- 인터랙티브 시뮬레이션 섹션 (검색 기반) ---
st.header("2. 미래 시뮬레이션: 지역별 침수 위험도 검색")

# 검색 가능한 도시 정보
LOCATIONS = {
    "인천": {"lat": 37.4563, "lon": 126.7052, "elev_m": 3.5, "zoom": 10},
    "부산": {"lat": 35.1796, "lon": 129.0756, "elev_m": 2.8, "zoom": 10},
    "목포": {"lat": 34.8118, "lon": 126.3922, "elev_m": 2.0, "zoom": 10},
    "투발루": {"lat": -8.5240, "lon": 179.1942, "elev_m": 1.5, "zoom": 11},
    "상하이": {"lat": 31.2304, "lon": 121.4737, "elev_m": 4.0, "zoom": 8},
    "베네치아": {"lat": 45.4408, "lon": 12.3155, "elev_m": 1.0, "zoom": 12},
    "뉴올리언스": {"lat": 29.9511, "lon": -90.0715, "elev_m": -0.5, "zoom": 9},
    "암스테르담": {"lat": 52.3702, "lon": 4.8952, "elev_m": -2.0, "zoom": 10}
}

search_term = st.text_input("도시 이름을 검색하여 침수 위험도를 확인하세요 (예: 인천, 부산, 투발루)", "")
cleaned_search = search_term.strip()

if cleaned_search:
    if cleaned_search in LOCATIONS:
        location_data = LOCATIONS[cleaned_search]

        st.subheader(f"'{cleaned_search}' 지역 시뮬레이션")
        sea_rise_m = st.slider(
            f"'{cleaned_search}'의 가상 해수면 상승 높이 (m)",
            0.0, 5.0, 1.0, step=0.1, key=f"slider_{cleaned_search}"
        )

        df_location = pd.DataFrame([location_data])
        df_location['inundated'] = df_location['elev_m'] <= sea_rise_m
        df_location['color'] = df_location['inundated'].apply(lambda x: [220, 20, 60] if x else [0, 114, 178])
        df_location['place'] = cleaned_search

        view_state = pdk.ViewState(
            latitude=location_data["lat"],
            longitude=location_data["lon"],
            zoom=location_data["zoom"],
            bearing=0,
            pitch=45
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_location,
            get_position='[lon, lat]',
            get_color='color',
            get_radius=5000,
            pickable=True
        )

        tooltip = {
            "html": "<b>{place}</b><br/>평균 해발고도: {elev_m} m<br/><b>침수 위험: {inundated}</b>",
            "style": {"backgroundColor": "#333", "color": "white"}
        }

        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style='mapbox://styles/mapbox/light-v9'
        )

        st.pydeck_chart(r)
        st.caption(f"'{cleaned_search}' 지역의 평균 해발고도는 약 {location_data['elev_m']}m 입니다. 해수면이 이보다 높아지면 붉은색 점으로 표시됩니다.")

    else:
        st.warning(f"'{cleaned_search}'에 대한 위치 정보가 없습니다. '인천', '부산', '투발루' 등으로 검색해보세요.")
else:
    st.info("도시 이름을 검색하면 해당 위치의 침수 시뮬레이션 지도가 나타납니다.")

st.divider()


# --- 결론 및 대처방안 ---
st.header("결론: 투발루의 절박함, 우리의 미래")
st.write("해수면 상승은 더 이상 먼 미래의 이야기가 아닌, 우리 눈앞에 닥친 현실입니다. 투발루의 절박한 외침은 곧 대한민국을 포함한 전 세계 해안 도시들이 마주할 미래의 경고입니다.")
st.divider()

st.header("우리가 선택해야 할 대처 방안")
with st.expander("🌍 온실가스 감축 (지구 온난화 완화)"):
    st.markdown("- **에너지 전환:** 화석 연료 사용을 줄이고 태양광, 풍력 등 신재생에너지 사용을 확대합니다.\n- **에너지 효율 개선:** 에너지 효율이 높은 제품 사용 및 건물 단열을 강화합니다.")
with st.expander("🛡️ 해안 지역 적응 및 보호"):
    st.markdown("- **물리적 방어:** 방파제 및 해안 방조제를 건설하여 침수를 막습니다.\n- **자연 기반 해법:** 맹그로브 숲, 갯벌 등 자연 해안선을 복원하여 파도를 완충합니다.")
with st.expander("🚶‍♂️ 개인의 일상 속 실천"):
    st.markdown("- **에너지 절약:** 불필요한 전등 끄기, 대중교통 이용 등 에너지 소비를 줄입니다.\n- **자원 재활용 및 소비 줄이기:** 불필요한 소비를 줄이고 분리배출을 철저히 합니다.")
st.divider()

st.header("제언: 미래를 위한 행동")
st.markdown("""
<p class="report-quote">
해수면 상승은 개인의 노력을 넘어, 공동의 목소리를 내는 적극적인 행동이 필요합니다. 학교 환경 동아리 활동이나 지역 사회의 환경 캠페인에 참여하여 더 많은 사람들의 관심과 동참을 이끌어내야 합니다.
</p>
""", unsafe_allow_html=True)

