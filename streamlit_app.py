# sea_level_dashboard_full.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pydeck as pdk
import requests
from io import StringIO

st.set_page_config(page_title="물러서는 땅, 다가오는 바다 — 해수면 상승 대시보드", layout="wide")
st.title("물러서는 땅, 다가오는 바다: 해수면 상승 대시보드")

# ====== 사이드바: 개요 및 투발루 사례 ======
st.sidebar.header("보고서 요약 & 투발루 사례")
st.sidebar.markdown("""
이 대시보드는 1900→2025(현재)까지의 지구 평균 해수면 변화를 보여주고,
사용자가 직접 데이터를 업로드하거나 슬라이더로 해수면 상승을 조작해 연안 취약도를 시각화할 수 있습니다.
""")

st.sidebar.subheader("투발루 (사례)")
st.sidebar.markdown("""
- 평균 해발고 약 2 m, 이미 수십 년간 해수면 상승과 침수 문제로 어려움을 겪어왔습니다.  
- 최근 수년간 호주 등으로의 이주·기후 비자 논의 및 신청이 활발해지고 있습니다(예: Falepili 관련 이민 방식 등).  
(보도·정책 동향 요약: Reuters/Wired 등).  
""")
st.sidebar.markdown("출처: Reuters, Wired 등 주요 보도 요약. :contentReference[oaicite:6]{index=6}")

st.markdown("""
### 사용법 (간단)
1. (선택) `data.go.kr`에서 CSV를 다운받아 업로드하면 해당 관측 데이터로 그래프가 갱신됩니다. (예: https://www.data.go.kr/data/15003326/fileData.do). :contentReference[oaicite:7]{index=7}  
2. 업로드가 없으면 '관측/재구성 시계열'을 자동 생성하여 1900–2025 그래프를 보여줍니다(교육/설명 목적의 추정치).  
3. 오른쪽의 '해수면 상승(m)' 슬라이더로 가상 상승을 조정하면 연안 취약도(샘플 도시/투발루)가 갱신됩니다.
""")

# ====== 데이터 로드 섹션 ======
st.header("데이터: 업로드 또는 자동(추정) 시계열")
uploaded = st.file_uploader("관측 CSV 업로드 (옵션) — data.go.kr에서 받으신 파일을 올려주세요", type=["csv","txt"])
use_remote_noaa = st.checkbox("NOAA/NASA 공개 시계열 자동 불러오기 시도 (가능하면)", value=False)

def build_estimated_gmsl():
    """
    교육용/설명용 추정 시계열 생성 (1900-2025).
    방법: 1900-1920~1992: 전세계 장기 평균 1.75 mm/yr(문헌 근거) 수준(근사),
           1993-2025: 위성시대 평균 ~3.3 mm/yr 구간으로 가속 반영.
    이 수치는 '정밀 관측' 대체가 아님 — 실제 관측치가 있으면 업로드/연동하세요.
    출처: 관측·재구성 연구 및 NOAA/NASA 개요. :contentReference[oaicite:8]{index=8}
    """
    years = np.arange(1900, 2026)
    gmsl_mm = np.zeros_like(years, dtype=float)
    # baseline: 1900 -> 0 mm (상대적)
    for i, y in enumerate(years):
        if y <= 1992:
            # 1900-1992: 평균 1.75 mm/yr (근사, 관측 기반 재구성 연구)
            gmsl_mm[i] = (y - 1900) * 1.75
        else:
            # 1993 onwards: 누적 전구간 (1900-1992) + (1993->y) * 3.3 mm/yr (위성시대 가속 반영)
            gmsl_mm[i] = (1992 - 1900) * 1.75 + (y - 1992) * 3.3
    df = pd.DataFrame({"year": years, "gmsl_mm": gmsl_mm})
    return df

df = None
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        st.success("업로드한 CSV 로드 완료 — 아래 미리보기(상위 10행)")
        st.dataframe(df.head(10))
        # 간단한 자동 컬럼 탐색: 'year'와 숫자 컬럼 찾기
        # (사용자가 올린 파일이 1900-2025 GMSL을 포함하면 이를 사용)
    except Exception as e:
        st.error(f"CSV 로드 오류: {e}")
        st.info("자동 생성 추정 시계열을 대신 사용합니다.")
        df = build_estimated_gmsl()
elif use_remote_noaa:
    # 시도: NOAA/NASA 공개 데이터 자동 가져오기 시도 (여건에 따라 실패 가능)
    st.info("원격 NOAA/NASA 시계열을 가져오려 시도합니다(인터넷 연결/URL 접근성에 따라 실패할 수 있음).")
    # 예시 시도 URL (여러 포맷 가능) — 실패 시 추정값 사용
    tried = False
    tried_urls = [
        # (주의: 실제 서비스의 CSV URL이 변경될 수 있으므로 예외 처리 중요)
        "https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/sl_lin_global.csv",
        "https://climate.nasa.gov/system/internal_resources/details/original/647_GlobalMeanSeaLevel.csv"
    ]
    for url in tried_urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.text) > 100:
                df = pd.read_csv(StringIO(r.text))
                st.success(f"원격 데이터 로드 성공: {url}")
                st.dataframe(df.head(10))
                tried = True
                break
        except Exception:
            continue
    if not tried:
        st.warning("원격 데이터 자동 로드 실패 — 내부 추정 시계열을 사용합니다.")
        df = build_estimated_gmsl()
else:
    st.info("업로드된 파일 없음 — 내부 추정 시계열을 사용합니다.")
    df = build_estimated_gmsl()

# 표준화: 내부 추정 또는 업로드 데이터가 'year' 와 'gmsl_mm' 형태가 아니면 시도 변환
if 'year' not in df.columns:
    # 유연 처리: 첫 숫자 컬럼을 year로 간주하거나 인덱스 사용
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) >= 1:
        # assume first numeric is year if plausible
        first = numeric_cols[0]
        if df[first].min() >= 1800 and df[first].max() <= 2100:
            df = df.rename(columns={first: 'year'})
    if 'year' not in df.columns:
        df = df.reset_index().rename(columns={'index': 'year'})

# 해수면 컬럼 찾기
gmsl_col = None
for c in df.columns:
    if 'sea' in c.lower() or 'gmsl' in c.lower() or 'level' in c.lower() or 'mm' in c.lower():
        gmsl_col = c
        break
if gmsl_col is None:
    # fallback: pick first numeric not year
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != 'year']
    if len(numeric_cols) > 0:
        gmsl_col = numeric_cols[0]
    else:
        st.error("해수면(숫자) 컬럼을 자동으로 찾지 못했습니다. 업로드한 CSV를 확인하세요.")
        st.stop()

# ====== 시계열 그래프와 숫자 ======
st.header("1900 → 2025: 지구 평균 해수면 (관측/추정)")
df_plot = df.copy()
# 필터 1900-2025
df_plot = df_plot[(df_plot['year'] >= 1900) & (df_plot['year'] <= 2025)].sort_values('year')
fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df_plot['year'], df_plot[gmsl_col], marker='o', linewidth=1.5)
ax.set_xlabel("Year")
ax.set_ylabel("Global Mean Sea Level (mm, baseline 1900=0)")
ax.set_title("Global Mean Sea Level: 1900 → 2025 (관측/추정)")
ax.grid(alpha=0.2)
st.pyplot(fig)

# 현재(2025) 기준 숫자 보여주기
latest = df_plot[df_plot['year'] == df_plot['year'].max()]
if not latest.empty:
    latest_val = float(latest[gmsl_col].values[0])
    st.metric(label=f"현재(연도 {int(latest['year'].values[0])}) 상대 해수면 상승", value=f"{latest_val:.1f} mm", delta=None)

# ====== 인터랙티브: 해수면 상승(m) 슬라이더로 연안 영향 데모 ======
st.header("인터랙션: 가정 해수면 상승을 직접 조작해보기")
sea_rise_m = st.slider("가정할 추가 해수면 상승 (m)", 0.0, 5.0, 0.5, step=0.1)
st.markdown("아래 표/지도는 **간단한 교육용 데모**입니다. 정밀 침수 예측은 DEM(지형고도), 조석, 지역 상대해수면 변화(RSL) 등 추가 데이터가 필요합니다.")

# 샘플 연안 도시 + 투발루 위치
sample = pd.DataFrame([
    {"place":"Funafuti (Tuvalu, capital atoll)", "lat":-8.5240, "lon":179.1942, "elev_m":1.5},
    {"place":"Incheon (Korea)", "lat":37.4563, "lon":126.7052, "elev_m":1.5},
    {"place":"Busan (Korea)", "lat":35.1796, "lon":129.0756, "elev_m":3.0},
    {"place":"Amsterdam (Netherlands)", "lat":52.3702, "lon":4.8952, "elev_m":-2.0},
    {"place":"Bangladesh coast (sample)", "lat":23.684994, "lon":90.356331, "elev_m":1.0},
])
sample['inundated_by_slider'] = sample['elev_m'] <= sea_rise_m
st.dataframe(sample.assign(elev_m=lambda d: d['elev_m'].map(lambda x: f"{x} m")))

# 지도: pydeck
sample['color'] = sample['inundated_by_slider'].apply(lambda x: [220, 30, 30] if x else [30, 120, 220])
mid = (sample['lat'].mean(), sample['lon'].mean())
layer = pdk.Layer(
    "ScatterplotLayer",
    data=sample,
    get_position='[lon, lat]',
    get_color='color',
    get_radius=80000,
    pickable=True
)
view = pdk.ViewState(latitude=mid[0], longitude=mid[1], zoom=2)
tooltip = {"text":"{place}\nelev: {elev_m} m\n침수(예측): {inundated_by_slider}"}
r = pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip)
st.pydeck_chart(r)

st.markdown("""
**해석:** 위 지도는 단순 비교(지역 평균 지면고 <= 가정 상승 높이 → '침수 가능')로 표시한 교육용 데모입니다.  
정밀한 침수 경계는 고해상 DEM·조석·해안구조물·지역 해수면 변동 등을 반영해야 합니다.
""")

# ====== 투발루 상세 정보 패널(최신 보도 요약 포함) ======
st.header("사례 심층: 투발루 (Tuvalu) — 현재 상황 요약")
st.markdown("""
- 투발루는 남태평양의 저평탄 섬나라로 평균 해발고가 약 2 m에 불과해 해수면 상승에 매우 취약합니다. :contentReference[oaicite:9]{index=9}  
- 최근 보도에 따르면 지난 30년간 약 15 cm 수준의 해수면 상승을 지역적으로 경험했으며, 호주 등으로의 이주·기후비자 프로그램 신청이 활발합니다. :contentReference[oaicite:10]{index=10}  
- 투발루 정부와 국제사회는 (1) 방파제·인공토지 조성, (2) 국제 이주 정책·비자 체계 협상, (3) 문화·주권 보전 전략(디지털 국가화 등)을 병행하고 있습니다. :contentReference[oaicite:11]{index=11}
""")

st.subheader("참고 보도(요약)")
st.markdown("""
- Reuters (2025): 투발루의 많은 주민이 호주의 기후 비자에 신청. 관측상 지난 수십년간 평균 해수면 상승이 지역에 큰 영향을 주고 있음. :contentReference[oaicite:12]{index=12}  
- Wired / Guardian 등(2025): 투발루의 계획된 이주 사례와 '국가 이주' 논의 관련 기사. :contentReference[oaicite:13]{index=13}
""")

# ====== 대처 방안 섹션 ======
st.header("대처 방안(요약) — 완화 + 적응 (정책·개인 실천)")
st.markdown("""
**1) 온실가스 감축(완화)**  
- 화석연료 사용 감축 → 재생에너지 전환, 에너지 효율화. (장기적으로 해수면 상승의 최악 시나리오 완화)

**2) 연안 적응(지역/공공)**  
- 자연 기반 해안 보호(맹그로브·갯벌 복원), 인공 방파제/방조제, 도시 재배치(Managed retreat), 안전한 이주 계획  
- 인프라·토지이용 계획(홍수 위험지역 개발 제한), 위기 대비 대피·이주 체계 구축

**3) 개인·학교·지역에서 할 수 있는 일**  
- 에너지 절약·저탄소 생활, 지역 환경 캠페인 참여, 데이터 기반 기후 교육 확산  
- 학생/지역사회 단위로 해수면·해안 변화를 모니터링하고 대응 방안(예: 학교 비상대응 계획) 수립
""")

st.markdown("더 정밀한 분석(예: DEM 기반 침수경계 계산, 지역별 인구 및 자산 피해 추정)을 원하시면 알려주세요. 해당 기능(DEM 연동·국토지리정보원 자료 활용)을 코드에 추가해 드립니다.")

# ====== 출처 안내 ======
st.header("데이터·정보 출처(주요)")
st.markdown("""
- 공공데이터포털: 해양환경공단 해양기후 변화 데이터 (파일/오픈API). :contentReference[oaicite:14]{index=14}  
- NASA Climate / Vital Signs (Global mean sea level 시계열 개요). :contentReference[oaicite:15]{index=15}  
- NOAA / NASA 연구 및 위성 관측(위성시대 상승률 관련). :contentReference[oaicite:16]{index=16}  
- 투발루 관련 최신 보도: Reuters, Wired, Guardian(2024–2025). :contentReference[oaicite:17]{index=17}
""")
