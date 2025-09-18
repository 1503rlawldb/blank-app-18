# sea_level_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk
from streamlit.components.v1 import iframe

st.set_page_config(page_title="물러서는 땅, 다가오는 바다 — 해수면 상승 대시보드", layout="wide")

st.title("물러서는 땅, 다가오는 바다: 해수면 상승 대시보드")
st.markdown("""
이 대시보드는  
- 공공데이터포털(해양환경공단)의 해양기후 변화 CSV 데이터를 사용한 시계열 시각화  
- KOEM 해수면상승 시뮬레이터(임베드)로 지역별 침수 시뮬레이션 직접 확인  
- 샘플 연안 도시(저해발 도시) 기반의 간단한 '침수 취약도 데모 맵'을 제공합니다.  
(정밀한 침수 예측은 고해상도 DEM/연안 지형 데이터 필요)  
""")

# 사이드바: 데이터 소스 설명 및 외부 링크
st.sidebar.header("데이터 소스")
st.sidebar.markdown("""
- 해양환경공단_해양기후 변화 정보 (공공데이터포털) — CSV / API 제공. (예시 데이터: 해수면·해수온 등 시계열). :contentReference[oaicite:1]{index=1}  
- KOEM 해수면상승 시뮬레이터 — 시나리오(RCP4.5/8.5), 연도별 시뮬레이션(2050/2100 등). (웹 툴을 대시보드에 임베드). :contentReference[oaicite:2]{index=2}
""")
st.sidebar.markdown("[공공데이터포털(데이터페이지) 열기](https://www.data.go.kr/data/15003326/fileData.do)")
st.sidebar.markdown("[KOEM 시뮬레이터 열기](https://www.koem.or.kr/simulation/gmsl/rcp45.do)")

st.header("1) 데이터 입력")
st.markdown("방법 A: 아래에서 CSV 파일 업로드 (data.go.kr에서 다운로드한 CSV를 업로드).  방법 B: 로컬 테스트용 샘플 사용")

uploaded = st.file_uploader("CSV 파일 업로드 (해양기후 변화 데이터)", type=["csv","txt"])
use_sample = st.checkbox("샘플 데이터로 실행 (빠른 데모)", value=False)

@st.cache_data
def load_sample_df():
    # 데모용 아주 단순한 해수면 시계열 샘플
    years = np.arange(1993, 2051)
    # 임의의 누적 해수면(단위: mm) 예시
    sl = 10 + 2*(years-1993) + np.random.normal(0, 1, len(years))
    df = pd.DataFrame({"year": years, "sea_level_mm": sl})
    return df

df = None
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        st.success("CSV 업로드 완료 — 상위 10개 행을 미리보기합니다.")
        st.dataframe(df.head(10))
    except Exception as e:
        st.error(f"CSV 읽기 오류: {e}")
elif use_sample:
    df = load_sample_df()
    st.info("샘플 데이터 사용 중")
    st.dataframe(df.head(10))
else:
    st.info("CSV를 업로드하거나 '샘플 데이터로 실행'을 체크하세요.")

# 데이터 시각화
if df is not None:
    st.header("2) 시계열: 해수면 변화(시연)")
    # 가능한 컬럼명 탐색(사용자 파일에 따라 다름)
    # 우선 'year'와 해수면 관련 컬럼을 자동 탐지
    year_col = None
    seacol = None
    for c in df.columns:
        if 'year' in c.lower() or '년도' in c:
            year_col = c
        if 'sea' in c.lower() or '해수' in c or 'sea_level' in c.lower() or 'msl' in c.lower():
            seacol = c
    # fallback
    if year_col is None:
        # 시퀀스 인덱스를 연도로 사용
        df = df.reset_index().rename(columns={'index':'year'})
        year_col = 'year'
    if seacol is None:
        # 샘플에서는 'sea_level_mm' 존재
        if 'sea_level_mm' in df.columns:
            seacol = 'sea_level_mm'
        else:
            # pick first numeric that's not year
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            numeric_cols = [c for c in numeric_cols if c != year_col]
            if len(numeric_cols)>0:
                seacol = numeric_cols[0]
            else:
                st.warning("해수면 컬럼을 자동으로 찾지 못했습니다. CSV를 확인해 주세요.")
    if seacol:
        # plot with matplotlib
        fig, ax = plt.subplots(figsize=(8,3.5))
        ax.plot(df[year_col], df[seacol], marker='o', linewidth=2)
        ax.set_xlabel("Year")
        ax.set_ylabel(f"{seacol}")
        ax.set_title("해수면(또는 선택한 숫자 컬럼) 시계열")
        ax.grid(alpha=0.25)
        st.pyplot(fig)

    # 요약 통계
    st.subheader("요약 통계")
    st.write(df[[year_col, seacol]].describe())

    # 사용자 입력: 시나리오용 슬라이더 (해수면 상승 임의값 적용)
    st.header("3) 연안 침수 취약도(샘플 데모)")
    st.markdown("**주의:** 정밀한 침수 시각화는 DEM(지형고도)·조위·파랑 등 복합 데이터 필요. 아래는 '간단한 데모'입니다.")
    sea_rise_m = st.slider("가정할 해수면 상승 (m)", min_value=0.0, max_value=5.0, value=0.5, step=0.1)

    # 샘플 연안 도시(위도,경도,평균지면고: m)
    sample_cities = pd.DataFrame([
        {"city":"Incheon", "lat":37.4563, "lon":126.7052, "elev_m":1.5},
        {"city":"Busan", "lat":35.1796, "lon":129.0756, "elev_m":3.0},
        {"city":"Mokpo", "lat":34.8110, "lon":126.3929, "elev_m":1.2},
        {"city":"Yeosu", "lat":34.7604, "lon":127.6623, "elev_m":2.0},
        {"city":"Gangneung", "lat":37.7519, "lon":128.8761, "elev_m":4.0},
    ])

    sample_cities['would_be_inundated'] = sample_cities['elev_m'] <= sea_rise_m
    st.dataframe(sample_cities)

    # Map with pydeck
    midpoint = (sample_cities['lat'].mean(), sample_cities['lon'].mean())
    # color by inundation
    sample_cities['color'] = sample_cities['would_be_inundated'].apply(lambda x: [255,0,0] if x else [0,128,255])
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=sample_cities,
        get_position='[lon, lat]',
        get_color='color',
        get_radius=5000,
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=midpoint[0], longitude=midpoint[1], zoom=5, pitch=0)
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text":"{city}\nelev: {elev_m} m\n침수: {would_be_inundated}"})
    st.pydeck_chart(r)

    st.markdown("""
    **해석 예시:** 위 표/맵은 '도시 평균 지면고 <= 가정 해수면 상승'이면 간단히 '침수 가능'으로 표기한 **매우 단순한 데모**입니다.
    실제 연안 침수 예측을 위해선 국토지리정보원의 DEM(표고), 해수위·조석, 기후 시나리오별 지역별 보정이 필요합니다.
    """)

# KOEM 시뮬레이터 임베드
st.header("4) KOEM 해수면상승 시뮬레이터 (직접 조작)")
st.markdown("아래 임베드 툴에서 시나리오(예: RCP4.5/RCP8.5), 연도(2050/2100), 슬라이더 등을 이용해 지역별 침수 시뮬레이션을 직접 보세요.")
# KOEM 페이지를 iframe으로 임베드 (서버 정책에 따라 임베딩이 막힐 수 있음)
koem_url = "https://www.koem.or.kr/simulation/gmsl/rcp45.do"
try:
    iframe(koem_url, height=700)
except Exception as e:
    st.error("브라우저/사이트의 임베딩 정책으로 임베드가 실패했습니다. 오른쪽 링크를 눌러 새 탭에서 열어주세요.")
    st.markdown(f"[KOEM 시뮬레이터 새탭에서 열기]({koem_url})")

st.header("마무리 및 사용팁")
st.markdown("""
- 정확한 연안 침수 예측을 하려면: **고해상 DEM(수미터 이하), 상세 연안형상, 기후 시나리오(지역 보정)** 등을 확보해야 합니다.  
- `data.go.kr`의 CSV(또는 오픈API)를 직접 불러오려면 해당 데이터의 '원문파일' 링크나 오픈API 키(발급 후)를 사용하세요. (공공데이터포털은 파일 다운로드 및 OpenAPI(JSON/XML) 제공). :contentReference[oaicite:3]{index=3}  
- KOEM 시뮬레이터는 이미 위의 요소들을 이용해 시뮬레이션한 결과를 보여주는 도구이므로, 대시보드에서 **임베드**해서 직접 값을 조작해보시면 교육용/설명용으로 매우 효과적입니다. :contentReference[oaicite:4]{index=4}
""")
