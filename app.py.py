import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# --- [1] 기본 설정 ---
st.set_page_config(page_title="공공 자전거 대시보드", layout="wide")
st.title("🚲 공공 자전거 데이터 분석 대시보드")
st.markdown("SQLite 데이터베이스와 Streamlit을 활용해 만든 첫 번째 대시보드입니다!")

# --- [2] 데이터베이스 확인 및 에러 처리 ---
DB_PATH = 'bicycle.db'

# bicycle.db 파일이 같은 폴더에 없으면 친절한 에러 메시지를 띄우고 멈춥니다.
if not os.path.exists(DB_PATH):
    st.error("🚨 앗! 데이터베이스 파일(`bicycle.db`)을 찾을 수 없어요!\n\n`app.py` 파일과 같은 폴더에 `bicycle.db` 파일이 있는지 꼭 확인해 주세요 🥺")
    st.stop()

# --- [3] 데이터 불러오기 함수 ---
# @st.cache_data는 데이터를 한 번만 불러와서 기억해두는 기능이에요. (속도 향상!)
@st.cache_data
def load_data(query):
    conn = sqlite3.connect(DB_PATH) # DB 연결
    df = pd.read_sql_query(query, conn) # SQL 쿼리로 데이터 가져와서 표(DataFrame)로 만들기
    conn.close() # DB 연결 종료
    return df

st.divider() # 구분선

# ==========================================
# 📊 첫 번째 차트: 월별 이용 패턴 (라인 차트)
# ==========================================
st.header("1. 월별 이용 패턴 📈")
query1 = """
SELECT 
    대여일자, 
    SUM(이용건수) AS 총이용건수
FROM 이용정보
GROUP BY 대여일자
ORDER BY 대여일자
"""
df1 = load_data(query1)

# 화면을 반으로 나누어 왼쪽엔 차트, 오른쪽엔 SQL을 보여줍니다.
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("① 시각화")
    # Plotly를 이용해 라인 차트를 그립니다.
    fig1 = px.line(df1, x='대여일자', y='총이용건수', markers=True, title="월별 총 이용건수")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("② 사용한 SQL 코드")
    st.code(query1, language='sql')

st.divider()

# ==========================================
# 📊 두 번째 차트: 기온별 평균 이용량 (막대 차트)
# ==========================================
st.header("2. 기온별 평균 이용량 🌡️")
query2 = """
SELECT 
    CAST(B.평균기온 / 5 AS INTEGER) * 5 || '도 구간' AS 기온구간,
    CAST(B.평균기온 / 5 AS INTEGER) * 5 AS 정렬용_기온,
    AVG(A.이용건수) AS 평균이용건수
FROM 이용정보 A
JOIN 기온 B ON A.대여일자 = B.년월
GROUP BY 기온구간, 정렬용_기온
ORDER BY 정렬용_기온
"""
df2 = load_data(query2)

col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("① 시각화")
    fig2 = px.bar(df2, x='기온구간', y='평균이용건수', title="기온 5도 구간별 평균 이용건수")
    st.plotly_chart(fig2, use_container_width=True)

with col4:
    st.subheader("② 사용한 SQL 코드")
    st.code(query2, language='sql')

st.divider()

# ==========================================
# 📊 세 번째 차트: 인기 대여소 TOP 10 (가로 막대 차트)
# ==========================================
st.header("3. 인기 대여소 TOP 10 🏆")
query3 = """
SELECT 
    B.보관소명,
    SUM(A.이용건수) AS 총이용건수
FROM 이용정보 A
JOIN 대여소 B ON A.대여소번호 = B.대여소번호
GROUP BY B.대여소번호, B.보관소명
ORDER BY 총이용건수 DESC
LIMIT 10
"""
df3 = load_data(query3)
# 가로 막대 차트에서 1등이 가장 위에 오도록 데이터를 뒤집어줍니다.
df3 = df3.sort_values(by='총이용건수', ascending=True)

col5, col6 = st.columns([1, 1])

with col5:
    st.subheader("① 시각화")
    fig3 = px.bar(df3, x='총이용건수', y='보관소명', orientation='h', title="총 이용건수 상위 10개 대여소")
    st.plotly_chart(fig3, use_container_width=True)

with col6:
    st.subheader("② 사용한 SQL 코드")
    st.code(query3, language='sql')