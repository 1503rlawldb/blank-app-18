# sea_level_dashboard_debug.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')   # 서버 환경에서 안전하게 그림 그리기
import matplotlib.pyplot as plt
import pydeck as pdk
from streamlit.components.v1 import iframe
import traceback
import sys
import io

st.set_page_config(page_title="해수면 상승 대시보드 (디버그 모드)", layout="wide")
st.title("물러서는 땅, 다가오는 바다 — (디버그 모드)")

st.markdown("문제가 발생하면 아래 '디버그 로그' 섹션에 예외 정보가 출력됩니다. ")

# 디버그 로그 저장 변수
debug_logs = io.StringIO()

def log(msg):
    print(msg)
    debug_logs.write(str(msg) + "\n")

try:
    st.header("데이터 입력")
    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv","txt"])
    use_sample = st.checkbox("샘플 데이터로 실행", value=False)

    @st.cache_data
    def load_sample_df():
        years = np.arange(1993, 2051)
        sl = 10 + 2*(years-1993) + np.random.normal(0, 1, len(years))
        df = pd.DataFrame({"year": years, "sea_level_mm": sl})
        return df

    df = None
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            st.success("CSV 업로드 완료")
            st.dataframe(df.head(10))
            log("CSV 로드 성공: 컬럼들 -> " + ", ".join(df.columns.astype(str).tolist()))
        except Exception as e:
            st.error("CSV 읽기 오류가 발생했습니다. 아래 디버그 로그를 확인하세요.")
            log("CSV 읽기 예외:")
            traceback.print_exc(file=debug_logs)
    elif use_sample:
        df = load_sample_df()
        st.info("샘플 데이터 사용 중")
        st.dataframe(df.head(10))
        log("샘플 데이터 로드됨")

    if df is not None:
        st.header("시계열 시각화")
        # 컬럼 자동 탐색 (더 튼튼하게)
        year_col = None
        seacol = None
        cols = [c.lower() for c in df.columns.astype(str)]
        for idx, c in enumerate(cols):
            if 'year' in c or '년도' in c or '연도' in c:
                year_col = df.columns[idx]
            if 'sea' in c or '해수' in c or 'msl' in c or '해수면' in c or 'level' in c:
                seacol = df.columns[idx]
        if year_col is None:
            # 인덱스를 year로 사용
            df = df.reset_index().rename(columns={'index':'year'})
            year_col = 'year'
            log("year 컬럼 없음 -> index를 year로 사용")
        if seacol is None:
            # 숫자 컬럼 중 첫 번째 사용
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            numeric_cols = [c for c in numeric_cols if c != year_col]
            if len(numeric_cols) > 0:
                seacol = numeric_cols[0]
                log(f"sea 컬럼 자동 선택: {seacol}")
            else:
                st.warning("해수면(숫자) 컬럼을 찾을 수 없습니다. CSV의 컬럼명을 확인하세요.")
                log("숫자 컬럼 없음 - 시각화 중단")
                raise ValueError("숫자형 해수면 컬럼 없음")

        # 그리기 (try로 감싸서 에러 발생 시 로그 출력)
        try:
            fig, ax = plt.subplots(figsize=(8,3.5))
            ax.plot(df[year_col], df[seacol], marker='o', linewidth=2)
            ax.set_xlabel("Year")
            ax.set_ylabel(f"{seacol}")
            ax.set_title("해수면(또는 선택한 숫자 컬럼) 시계열")
            ax.grid(alpha=0.25)
            st.pyplot(fig)
        except Exception as e:
            st.error("시각화 중 오류가 발생했습니다. 디버그 로그를 확인하세요.")
            traceback.print_exc(file=debug_logs)
            raise

        st.subheader("요약 통계")
        st.write(df[[year_col, seacol]].describe())

        st.header("연안 취약도 데모")
        sea_rise_m = st.slider("가정 해수면 상승 (m)", 0.0, 5.0, 0.5, 0.1)
        sample_cities = pd.DataFrame([
            {"city":"Incheon", "lat":37.4563, "lon":126.7052, "elev_m":1.5},
            {"city":"Busan", "lat":35.1796, "lon":129.0756, "elev_m":3.0},
            {"city":"Mokpo", "lat":34.8110, "lon":126.3929, "elev_m":1.2},
        ])
        sample_cities['would_be_inundated'] = sample_cities['elev_m'] <= sea_rise_m
        sample_cities['color'] = sample_cities['would_be_inundated'].apply(lambda x: [255,0,0] if x else [0,128,255])
        st.dataframe(sample_cities)

        try:
            midpoint = (sample_cities['lat'].mean(), sample_cities['lon'].mean())
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
        except Exception:
            st.error("지도 렌더링 중 오류 발생 (pydeck 관련). 디버그 로그 확인.")
            traceback.print_exc(file=debug_logs)

    # KOEM 임베드 (예외 처리)
    st.header("KOEM 시뮬레이터 임베드")
    koem_url = "https://www.koem.or.kr/simulation/gmsl/rcp45.do"
    try:
        iframe(koem_url, height=700)
    except Exception:
        st.warning("임베드 실패 — 사이트의 임베딩 정책 때문일 수 있습니다. 아래 링크로 새 탭에서 열어보세요.")
        st.markdown(f"[KOEM 시뮬레이터 새탭에서 열기]({koem_url})")
        traceback.print_exc(file=debug_logs)

except Exception as e:
    st.error("대시보드 실행 중 예외가 발생했습니다. 아래 디버그 로그를 확인하세요.")
    log("최상위 예외:")
    traceback.print_exc(file=debug_logs)

# 디버그 로그 패널 (항상 보이게)
st.header("디버그 로그")
st.text_area("로그", value=debug_logs.getvalue(), height=300)
