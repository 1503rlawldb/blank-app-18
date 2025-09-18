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

# --- 커스텀 스타일 적용 ---
st.markdown("""
<style>
/* Streamlit 앱의 메인 배경 및 폰트 */
.stApp {
    background-color: #0c1445; /* 깊은 바다색 */
    color: #e0e0e0;
    font-family: 'Noto Sans KR', sans-serif;
}

/* 헤더와 제목 스타일 */
h1 {
    font-size: 2.8rem;
    color: #ffffff;
    text-align: center;
    text-shadow: 2px 2px 4px #000000;
}
h2 {
    font-size: 2rem;
    color: #61dafb; /* 밝은 하늘색 포인트 */
    border-bottom: 2px solid #61dafb;
    padding-bottom: 10px;
    margin-top: 40px;
}
h3 {
    font-size: 1.5rem;
    color: #ffffff;
    margin-top: 30px;
}

/* 본문 텍스트 스타일 */
p, li {
    font-size: 1.1rem;
    line-height: 1.8;
}

/* 인용구 또는 강조 블록 스타일 */
.report-quote {
    background-color: rgba(255, 255, 255, 0.05);
    border-left: 5px solid #61dafb;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
    font-style: italic;
}

/* 사이드바 스타일 */
.st-emotion-cache-16txtl3 {
    background-color: rgba(0, 0, 0, 0.2);
}

</style>
""", unsafe_allow_html=True)

# --- 제목 ---
st.markdown("<h1>물러서는 땅, 다가오는 바다</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #a0a0a0;'>해수면 상승 인터랙티브 대시보드</h3>", unsafe_allow_html=True)
st.divider()

# --- 서론 (기존 보고서 내용) ---
st.header("서론: 우리 눈앞에 닥친 현실")
st.markdown("""
<p class="report-quote">
인류의 기술이 나날이 발전함과 동시에 세상은 황폐해져 가고 있습니다.<br>
기온은 해마다 오르고, 북극과 남극의 빙하는 녹아내리며, 남극에서는 아름다운 꽃을 볼 수 있게 되었습니다. 바다는 따뜻해지고 해수면은 조용히 그러나 확실하게 높아지고 있습니다.
</p>
""", unsafe_allow_html=True)
st.write("지금 이 순간에도 우리 삶의 터전은 서서히 잠식당하고 있는 것입니다. 이 대시보드는 해수면 상승의 심각성을 데이터로 직접 확인하고, 미래의 위험을 시뮬레이션하며, 우리가 나아가야 할 길을 함께 고민하고자 합니다.")
st.divider()

# --- 데이터 로드 및 시각화 섹션 ---
st.header("1. 과거와 현재: 해수면 상승 데이터 분석")

# --- 데이터 로드 로직 ---
def build_estimated_gmsl():
    """ 교육용/설명용 추정 시계열 생성 (1900-2025) """
    years = np.arange(1900, 2026)
    gmsl_mm = np.zeros_like(years, dtype=float)
    for i, y in enumerate(years):
        if y <= 1992:
            gmsl_mm[i] = (y - 1900) * 1.75
        else:
            gmsl_mm[i] = (1992 - 1900) * 1.75 + (y - 1992) * 3.4
    df = pd.DataFrame({"year": years, "gmsl_mm": gmsl_mm})
    return df

# Streamlit의 컬럼 기능을 사용하여 UI 구성
col1, col2 = st.columns(2)

with col1:
    st.subheader("데이터 선택")
    st.info("아래 옵션을 선택하여 해수면 데이터를 불러올 수 있습니다. 선택하지 않으면 1900-2025년 추정치가 자동으로 표시됩니다.")
    uploaded_file = st.file_uploader("CSV 업로드 (data.go.kr)", type=["csv", "txt"])
    use_remote_noaa = st.checkbox("NOAA/NASA 공개 데이터 자동 불러오기 (권장)", value=True)

df = None
if uploaded_file is not None:
    try:
        # data.go.kr에서 받은 파일은 한글 인코딩 문제가 있을 수 있음
        df = pd.read_csv(uploaded_file, encoding='cp949')
        # '연평균' 컬럼명을 표준화
        if '연평균(cm)' in df.columns:
            df['gmsl_mm'] = df['연평균(cm)'] * 10
        if '연도' in df.columns:
            df = df.rename(columns={'연도': 'year'})
        st.success("업로드한 CSV 로드 완료!")
    except Exception as e:
        st.error(f"CSV 로드 오류: {e}. 인코딩을 확인하거나 다른 파일을 사용해주세요.")
        df = build_estimated_gmsl()

elif use_remote_noaa:
    url = "https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/slr/slr_sla_gbl_free_txj1j2_90.csv"
    try:
        response = requests.get(url)
        csv_data = StringIO(response.text)
        df_noaa = pd.read_csv(csv_data, header=1)
        # NOAA 데이터 가공
        df_noaa = df_noaa.rename(columns={'year': 'year', 'TOPEX/Poseidon': 'gmsl_mm'})
        # 1993년 이전 데이터와 결합하기 위해 기준점 조정
        df_estimated = build_estimated_gmsl()
        df_noaa['gmsl_mm'] = df_noaa['gmsl_mm'] - df_noaa['gmsl_mm'].iloc[0] + df_estimated[df_estimated['year']==1993]['gmsl_mm'].iloc[0]
        df = df_noaa[['year', 'gmsl_mm']]
        st.success("NOAA 위성 데이터 로드 완료!")
    except Exception:
        st.warning("원격 데이터 로드 실패. 내부 추정 시계열을 사용합니다.")
        df = build_estimated_gmsl()
else:
    df = build_estimated_gmsl()

# 데이터프레임 표준화 및 gmsl_mm 컬럼 찾기
if 'year' not in df.columns:
    year_like_col = [c for c in df.columns if 'year' in str(c).lower() or '연도' in str(c)]
    if year_like_col:
        df = df.rename(columns={year_like_col[0]: 'year'})
    else:
        df = df.reset_index().rename(columns={'index':'year'}) # Fallback

if 'gmsl_mm' not in df.columns:
    level_like_col = [c for c in df.columns if 'level' in str(c).lower() or 'gmsl' in str(c).lower() or '해수면' in str(c) or '연평균' in str(c)]
    if level_like_col:
        df = df.rename(columns={level_like_col[0]:'gmsl_mm'})
    else:
        # Fallback to first numeric column
        numeric_cols = df.select_dtypes(include=np.number).columns
        if len(numeric_cols) > 1:
            df = df.rename(columns={numeric_cols[1]:'gmsl_mm'})

# --- 데이터 시각화 ---
with col2:
    st.subheader("지구 평균 해수면 변화 (1900-현재)")
    df_plot = df.copy()
    df_plot = df_plot[(df_plot['year'] >= 1900) & (df_plot['year'] <= 2025)].sort_values('year')
    
    # 1900년 값을 0으로 기준점 조정
    df_plot['gmsl_mm'] = df_plot['gmsl_mm'] - df_plot[df_plot['year'] == 1900]['gmsl_mm'].iloc[0] if 1900 in df_plot['year'].values else df_plot['gmsl_mm'] - df_plot['gmsl_mm'].iloc[0]
    
    st.line_chart(df_plot.rename(columns={'year':'index'}).set_index('index')['gmsl_mm'], color="#ff4b4b")
    
    latest_year = int(df_plot['year'].max())
    latest_val = float(df_plot[df_plot['year'] == latest_year]['gmsl_mm'].values[0])
    st.metric(label=f"{latest_year}년 기준 상대 해수면 상승", value=f"{latest_val:.1f} mm", delta=f"{latest_val - float(df_plot[df_plot['year'] == latest_year-1]['gmsl_mm'].values[0]):.1f} mm (전년 대비)")

st.caption("그래프: 1900년 대비 지구 평균 해수면 높이 변화(mm). 데이터는 선택된 소스(업로드/NOAA/추정치)를 기반으로 합니다.")
st.divider()

# --- 인터랙티브 시뮬레이션 섹션 ---
st.header("2. 미래 시뮬레이션: 해수면 상승 영향 분석")
sea_rise_m = st.slider("가상으로 해수면을 높여보세요 (단위: m)", 0.0, 5.0, 1.0, step=0.1)
st.markdown("오른쪽 슬라이더를 조작하면, 설정한 높이보다 평균 해발고도가 낮은 주요 지역들이 지도에 붉게 표시됩니다.")

# 샘플 도시 데이터
sample_cities = pd.DataFrame([
    {"place":"투발루 푸나푸티", "lat":-8.5240, "lon":179.1942, "elev_m":1.5},
    {"place":"대한민국 인천", "lat":37.4563, "lon":126.7052, "elev_m":3.5},
    {"place":"대한민국 부산", "lat":35.1796, "lon":129.0756, "elev_m":2.8},
    {"place":"네덜란드 암스테르담", "lat":52.3702, "lon":4.8952, "elev_m":-2.0},
    {"place":"베트남 호치민", "lat":10.8231, "lon":106.6297, "elev_m":1.5},
    {"place":"미국 뉴올리언스", "lat":29.9511, "lon":-90.0715, "elev_m":-0.5}
])
sample_cities['inundated'] = sample_cities['elev_m'] <= sea_rise_m
sample_cities['color'] = sample_cities['inundated'].apply(lambda x: [220, 20, 60] if x else [30, 144, 255])

# Pydeck 지도 시각화
mid_point = (sample_cities['lat'].mean(), sample_cities['lon'].mean())
layer = pdk.Layer(
    "ScatterplotLayer",
    data=sample_cities,
    get_position='[lon, lat]',
    get_color='color',
    get_radius=80000,
    pickable=True
)
view_state = pdk.ViewState(latitude=mid_point[0], longitude=mid_point[1], zoom=1, bearing=0, pitch=0)
tooltip = {"html": "<b>{place}</b><br/>평균 해발고도: {elev_m} m<br/><b>침수 위험: {inundated}</b>", "style": {"color": "white"}}
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip, map_style='mapbox://styles/mapbox/dark-v9')
st.pydeck_chart(r)
st.caption("주의: 위 지도는 단순 '평균 해발고도' 비교를 통한 교육용 데모이며, 실제 침수 범위는 조석, 지형, 방어 시설 등에 따라 달라집니다.")
st.divider()

# --- 본론/결론/대처방안 (기존 보고서 내용) ---
# --- 본론 2 ---
st.header("사례 연구: 이미 시작된 재앙, 투발루의 눈물")
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://img.hani.co.kr/imgdb/original/2021/1109/20211109502389.jpg",
             caption="2021년, 물에 잠긴 국토에서 연설하는 투발루 외교장관")
with col2:
    st.subheader("사라지는 섬나라, 투발루")
    st.write("투발루는 평균 해발고도가 2~3m에 불과하여 해수면 상승에 가장 큰 위협을 받고 있습니다. 바닷물 유입으로 농경지와 식수원이 오염되고, 주민들은 '환경 난민'이 되어 이주를 고민하고 있습니다. 투발루의 현실은 해수면 상승이 단순한 환경 문제를 넘어 국가의 생존과 인간의 존엄성까지 위협하는 재앙임을 보여줍니다.")

st.divider()
# --- 결론 ---
st.header("결론: 투발루의 절박함, 우리의 미래")
st.write("해수면 상승은 더 이상 먼 미래의 이야기가 아닌, 우리 눈앞에 닥친 현실입니다. 투발루의 절박한 외침은 곧 대한민국을 포함한 전 세계 해안 도시들이 마주할 미래의 경고입니다.")
st.divider()
# --- 대처 방안 ---
st.header("우리가 선택해야 할 대처 방안")
with st.expander("🌍 온실가스 감축 (지구 온난화 완화)"):
    st.markdown("- **에너지 전환:** 화석 연료 사용을 줄이고 태양광, 풍력 등 신재생에너지 사용을 확대합니다.\n- **에너지 효율 개선:** 에너지 효율이 높은 제품 사용 및 건물 단열을 강화합니다.")
with st.expander("🛡️ 해안 지역 적응 및 보호"):
    st.markdown("- **물리적 방어:** 방파제 및 해안 방조제를 건설하여 침수를 막습니다.\n- **자연 기반 해법:** 맹그로브 숲, 갯벌 등 자연 해안선을 복원하여 파도를 완충합니다.")
with st.expander("🚶‍♂️ 개인의 일상 속 실천"):
    st.markdown("- **에너지 절약:** 불필요한 전등 끄기, 대중교통 이용 등 에너지 소비를 줄입니다.\n- **자원 재활용 및 소비 줄이기:** 불필요한 소비를 줄이고 분리배출을 철저히 합니다.")
st.divider()
# --- 제언 ---
st.header("제언: 미래를 위한 행동")
st.markdown("""
<p class="report-quote">
해수면 상승은 개인의 노력을 넘어, 공동의 목소리를 내는 적극적인 행동이 필요합니다. 학교 환경 동아리 활동이나 지역 사회의 환경 캠페인에 참여하여 더 많은 사람들의 관심과 동참을 이끌어내야 합니다.
</p>
""", unsafe_allow_html=True)
