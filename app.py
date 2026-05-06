import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# --- [1] 기본 설정 ---
st.set_page_config(page_title="자치구별 따릉이 경영 분석", layout="wide")
st.title("🚲 자치구별 공공 자전거 이용 패턴 분석")
st.markdown("자치구별 이용 차이를 분석하여 **자산 최적화** 및 **ESG 경영** 인사이트를 도출합니다.")

# --- [2] 데이터베이스 확인 및 에러 처리 ---
DB_PATH = 'bicycle.db'

if not os.path.exists(DB_PATH):
    st.error("🚨 `bicycle.db` 파일을 찾을 수 없어요! 파일 위치를 확인해 주세요.")
    st.stop()

# --- [3] 데이터 불러오기 함수 ---
@st.cache_data
def load_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.divider()

# ==========================================
# 📊 분석 1: 자치구별 이용 효율성 (자산 최적화)
# ==========================================
st.header("1. 자치구별 이용 건수 및 효율성 분석 🏢")
st.info("💡 **경영 인사이트:** 이용 건수가 특정 구에 편중되어 있다면, 자전거 재배치(Logistics) 우선순위를 조정하여 유휴 자산을 줄이고 회전율을 높여야 합니다.")

query1 = """
SELECT 
    B.자치구, 
    SUM(A.이용건수) AS 총이용건수
FROM 이용정보 A
JOIN 대여소 B ON A.대여소번호 = B.대여소번호
GROUP BY B.자치구
ORDER BY 총이용건수 DESC
"""
df1 = load_data(query1)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("① 시각화")
    fig1 = px.pie(df1, values='총이용건수', names='자치구', title="자치구별 이용 비중", hole=0.3)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("② 사용한 SQL 코드")
    st.code(query1, language='sql')

st.divider()

# ==========================================
# 📊 분석 2: 자치구별 이용 페르소나 (마케팅 전략)
# ==========================================
st.header("2. 이동거리 vs 이용시간 상관분석 🗺️")
st.info("💡 **경영 인사이트:** 평균 이동거리가 길면 '레저형', 짧으면 '통근/단거리 이동형'으로 분류합니다. 지역 특성에 맞춘 차별화된 마케팅 메시지가 필요합니다.")

query2 = """
SELECT 
    B.자치구, 
    AVG(A.이동거리) AS 평균이동거리, 
    AVG(A.이용시간) AS 평균이용시간,
    SUM(A.이용건수) AS 총이용건수
FROM 이용정보 A
JOIN 대여소 B ON A.대여소번호 = B.대여소번호
GROUP BY B.자치구
"""
df2 = load_data(query2)

col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("① 시각화")
    # 자치구별 특성을 한눈에 보는 버블 차트
    fig2 = px.scatter(df2, x="평균이동거리", y="평균이용시간", 
                 size="총이용건수", color="자치구",
                 hover_name="자치구", title="자치구별 이용 성격(레저 vs 통근)",
                 labels={"평균이동거리": "평균 이동거리(m)", "평균이용시간": "평균 이용시간(분)"})
    st.plotly_chart(fig2, use_container_width=True)

with col4:
    st.subheader("② 사용한 SQL 코드")
    st.code(query2, language='sql')

st.divider()

# ==========================================
# 📊 분석 3: 자치구별 ESG 기여도 (지속가능경영)
# ==========================================
st.header("3. 자치구별 탄소 절감 성과 🌿")
st.info("💡 **경영 인사이트:** 각 자치구의 탄소 절감량을 수치화하여 지자체 협력 사업의 근거로 활용하거나 ESG 경영 보고서의 핵심 지표로 사용할 수 있습니다.")

query3 = """
SELECT 
    B.자치구, 
    SUM(A.탄소량) AS 총탄소절감량
FROM 이용정보 A
JOIN 대여소 B ON A.대여소번호 = B.대여소번호
GROUP BY B.자치구
ORDER BY 총탄소절감량 ASC
"""
df3 = load_data(query3)

col5, col6 = st.columns([1, 1])

with col5:
    st.subheader("① 시각화")
    fig3 = px.bar(df3, x='총탄소절감량', y='자치구', orientation='h', 
             title="자치구별 누적 탄소 절감량",
             color='총탄소절감량', color_continuous_scale='Greens')
    st.plotly_chart(fig3, use_container_width=True)

with col6:
    st.subheader("② 사용한 SQL 코드")
    st.code(query3, language='sql')
