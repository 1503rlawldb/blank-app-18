import streamlit as st
import pandas as pd
import numpy as np

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

/* 이미지 캡션 스타일 */
.stImage > figcaption {
    text-align: center;
    color: #a0a0a0;
}

/* 버튼 스타일 */
.stButton > button {
    border: 2px solid #61dafb;
    border-radius: 20px;
    color: #61dafb;
    background-color: transparent;
}
.stButton > button:hover {
    border-color: #ffffff;
    color: #ffffff;
    background-color: #61dafb;
}

</style>
""", unsafe_allow_html=True)

# --- 보고서 내용 시작 ---

# --- 제목 ---
st.markdown("<h1>물러서는 땅, 다가오는 바다</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #a0a0a0;'>해수면 상승의 위험과 우리만의 대처법</h3>", unsafe_allow_html=True)
st.divider()

# --- 서론 ---
st.header("서론: 우리 눈앞에 닥친 현실")
st.markdown("""
<p class="report-quote">
인류의 기술이 나날이 발전함과 동시에 세상은 황폐해져 가고 있습니다.<br>
기온은 해마다 오르고, 북극과 남극의 빙하는 녹아내리며, 남극에서는 아름다운 꽃을 볼 수 있게 되었습니다. 바다는 따뜻해지고 해수면은 조용히 그러나 확실하게 높아지고 있습니다.
</p>
""", unsafe_allow_html=True)
st.write("""
지금 이 순간에도 우리 삶의 터전은 서서히 잠식당하고 있는 것입니다.
이 보고서는 아직 해수면 상승의 심각성을 와닿지 못하는 청소년들에게 그 위험을 알리고, 우리가 반드시 선택해야 할 대처 방안을 제시하고자 합니다. 훗날 가까운 미래에 세상을 이끌어 갈 청소년 여러분이 이 문제를 외면한다면, 결국 그 피해는 여러분의 세대가 고스란히 떠안게 될 것입니다.
""")

# --- 설문 자료 시각화 ---
st.subheader("청소년 인식 설문 (가상 데이터)")
st.write("청소년들은 아직 해수면 상승의 문제에 대해 정확하게 인지하지 못하고 있으며, 지금부터 이 보고서를 통해 그 현실이 우리에게도 멀지 않았음을 알려주려 합니다.")

# 가상 데이터 생성
chart_data = pd.DataFrame({
    '응답': ['매우 심각', '어느 정도 심각', '보통', '심각하지 않음', '전혀 모름'],
    '비율 (%)': [15, 35, 25, 15, 10]
})
st.bar_chart(chart_data.set_index('응답'), color="#61dafb")
st.caption("그래프: '해수면 상승 문제의 심각성을 체감하십니까?'에 대한 가상 설문 결과")
st.divider()


# --- 본론 1 ---
st.header("본론 1: 데이터가 경고하는 미래")
st.subheader("2050년, 물에 잠길 대한민국과 세계")
st.image("https://assets.climatecentral.org/images/made/5-2-22_KR_Incheon_Airport_comparison_map_1050_665_80_s_c1.jpg",
         caption="NASA의 데이터를 기반으로 Climate Central이 예측한 2050년 인천국제공항 일대의 침수 예상도")

st.write("""
위 지도는 2050년을 가정해 해수면 상승으로 잠기게 될 대한민국의 주요 도시와 세계 각국의 연안을 보여줍니다. 단순한 그림이 아니라, 과학적 데이터와 시뮬레이션을 바탕으로 만들어진 미래의 경고장입니다. 인천과 전라도의 주요 도시들 뿐 아니라 세계의 수많은 항구 도시들이 물속에 잠길 수 있다는 사실은 더 이상 영화 속 상상이 아닙니다.

지금 우리가 아무런 행동을 하지 않는다면, 2050년의 이 지도는 ‘예상도’가 아니라 ‘현실의 풍경’이 될 것입니다. 결국 그 피해를 고스란히 짊어지게 되는 세대가 바로 여러분입니다. 따라서 지금 이 순간부터 기후 변화와 해수면 상승 문제를 ‘내 문제’로 인식하고, 일상 속 작은 실천부터 시작해야 합니다.
""")
st.divider()

# --- 본론 2 ---
st.header("본론 2: 이미 시작된 재앙, 투발루의 눈물")
st.write("""
해수면 상승은 단순한 자연 현상이 아니라 실제로 여러 나라에서 심각한 피해를 일으키고 있습니다. 이러한 피해 사건들을 살펴보면 해수면 상승이 우리 생활과 안전에 어떤 영향을 주는지 더 잘 알 수 있습니다.
""")

col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://img.hani.co.kr/imgdb/original/2021/1109/20211109502389.jpg",
             caption="2021년, 물에 잠긴 국토에서 기후변화협약 당사국총회(COP26) 영상 연설을 하는 투발루 외교장관")

with col2:
    st.subheader("사라지는 섬나라, 투발루")
    st.write("""
    투발루는 남태평양에 있는 작은 섬나라로, 평균 해발고도가 2~3m밖에 되지 않아 해수면 상승에 가장 큰 위협을 받고 있습니다. 실제로 바닷물이 섬 마을로 밀려들어와 농경지가 침수되고 식수원이 오염되는 일이 자주 발생합니다.

    이 때문에 주민들이 살 곳을 잃고, 호주나 뉴질랜드 등으로 이주하는 ‘환경 난민’ 문제가 생기고 있습니다. 전문가들은 앞으로 해수면이 계속 높아진다면 투발루라는 나라 자체가 지도에서 사라질 수 있다고 경고하고 있습니다. 21세기 아틀란티스로 불리는 이유입니다.
    
    투발루는 현재 여러 나라들에게 자국민의 대한 이민을 요청하였으나 거부당하고 있는 안타까운 상황에 처해있습니다.
    """)
st.divider()

# --- 결론 ---
st.header("결론: 투발루의 절박함, 우리의 미래")
st.write("""
해수면 상승은 더 이상 먼 미래의 이야기가 아닌, 우리 눈앞에 닥친 현실입니다. 남태평양의 작은 섬나라 투발루는 해수면 상승의 가장 비극적인 예시를 보여줍니다. 평균 해발고도가 2~3m에 불과한 이 나라는 국토 전체가 물에 잠길 위기에 처해 있으며, 이로 인해 국민들은 삶의 터전을 잃고 '환경 난민'으로 전락할 위기에 놓였습니다.

투발루의 대통령이 직접 물에 잠긴 곳에서 연설하며 국제 사회에 도움을 호소하고 있지만, 여러 국가로부터 이민 요청이 거부당하는 안타까운 현실은 해수면 상승이 단순한 환경 문제를 넘어 국가의 생존과 인간의 존엄성까지 위협하는 심각한 재앙임을 명백히 보여줍니다. 투발루의 절박한 외침은 곧 대한민국을 포함한 전 세계 해안 도시들이 마주할 미래의 경고입니다.
""")
st.divider()


# --- 대처 방안 ---
st.header("우리가 선택해야 할 대처 방안")

with st.expander("🌍 온실가스 감축 (지구 온난화 완화)"):
    st.markdown("""
    - **에너지 전환:** 화석 연료(석탄, 석유) 사용을 줄이고 태양광, 풍력 등 신재생에너지 사용을 확대합니다.
    - **에너지 효율 개선:** 에너지 효율이 높은 제품을 사용하고, 건물 단열을 강화하여 불필요한 에너지 소비를 줄입니다.
    """)

with st.expander("🛡️ 해안 지역 적응 및 보호"):
    st.markdown("""
    - **방파제 및 해안 방조제 건설:** 해안 지역에 물리적인 방어벽을 설치하여 침수를 막습니다.
    - **자연 해안선 복원:** 맹그로브 숲, 갯벌 등 자연적인 해안 방어선을 복원하고 조성하여 파도의 영향을 완충합니다.
    - **연안 관리 계획 수립:** 해수면 상승에 취약한 지역의 개발을 제한하고, 주민들의 안전한 이주 계획을 미리 수립합니다.
    """)

with st.expander("🚶‍♂️ 개인의 일상 속 실천"):
    st.markdown("""
    - **에너지 절약:** 사용하지 않는 전등을 끄고, 대중교통을 이용하는 등 일상생활에서 에너지 소비를 줄입니다.
    - **자원 재활용 및 소비 줄이기:** 불필요한 소비를 줄이고, 쓰레기 분리배출을 철저히 하여 자원의 낭비를 막습니다.
    - **환경 문제에 대한 관심과 참여:** 기후 변화와 해수면 상승 문제의 심각성을 인지하고, 관련 정책이나 캠페인에 관심을 갖고 참여합니다.
    """)
st.divider()

# --- 제언 ---
st.header("제언: 미래를 위한 행동")
st.markdown("""
<p class="report-quote">
해수면 상승은 개인의 노력을 넘어, 공동의 목소리를 내는 적극적인 행동이 필요합니다. 학교 환경 동아리 활동이나 지역 사회의 환경 캠페인에 참여하여 더 많은 사람들의 관심과 동참을 이끌어내야 합니다.
</p>
""", unsafe_allow_html=True)
