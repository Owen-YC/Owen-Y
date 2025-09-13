import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json
import time
from datetime import datetime, timedelta
import pytz
import numpy as np
from typing import Dict, List, Optional
import os

# 페이지 설정
st.set_page_config(
    page_title="✈️ FlightAware Tracker",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FlightAware CSS - Modern Aviation Theme
st.markdown("""
<style>
    /* 전체 배경 - 항공 테마 */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        min-height: 100vh;
    }
    
    /* 메인 컨테이너 */
    .main-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* 카드 디자인 */
    .flight-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .flight-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    /* 제목 스타일 */
    .main-title {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
    }
    
    /* 섹션 제목 */
    .section-title {
        color: #f1f5f9;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        padding-left: 1rem;
        border-left: 4px solid #3b82f6;
    }
    
    /* 메트릭 스타일 */
    .metric-container {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
    }
    
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
    }
    
    /* 테이블 스타일 */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* 애니메이션 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* 로딩 스피너 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(59, 130, 246, 0.3);
        border-radius: 50%;
        border-top-color: #3b82f6;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# FlightAware API 설정 (시뮬레이션 모드)
class FlightAwareAPI:
    def __init__(self):
        self.api_key = os.getenv("FLIGHTAWARE_API_KEY")
        self.base_url = "https://flightxml.flightaware.com/json/FlightXML2"
        
    def get_flight_info(self, flight_number: str) -> Dict:
        """항공편 정보 조회 (시뮬레이션)"""
        # 실제 API 호출 대신 시뮬레이션 데이터 반환
        return {
            "flight_number": flight_number,
            "airline": self._get_airline_from_code(flight_number[:2]),
            "aircraft": "Boeing 737-800",
            "departure": {
                "airport": "ICN",
                "airport_name": "인천국제공항",
                "city": "서울",
                "country": "대한민국",
                "scheduled_time": "14:30",
                "actual_time": "14:35",
                "gate": "A12",
                "terminal": "T1"
            },
            "arrival": {
                "airport": "NRT",
                "airport_name": "나리타국제공항",
                "city": "도쿄",
                "country": "일본",
                "scheduled_time": "17:45",
                "actual_time": "17:40",
                "gate": "B8",
                "terminal": "T1"
            },
            "status": "On Time",
            "duration": "2시간 10분",
            "distance": "1,300 km"
        }
    
    def get_airport_departures(self, airport_code: str) -> List[Dict]:
        """공항 출발편 조회 (시뮬레이션)"""
        flights = []
        airlines = ["KE", "OZ", "JL", "NH", "CA", "MU", "SQ", "TG"]
        destinations = ["NRT", "HND", "PEK", "PVG", "SIN", "BKK", "LAX", "JFK"]
        
        for i in range(10):
            airline = np.random.choice(airlines)
            dest = np.random.choice(destinations)
            flight_num = f"{airline}{np.random.randint(100, 9999)}"
            
            flights.append({
                "flight_number": flight_num,
                "airline": self._get_airline_from_code(airline),
                "destination": dest,
                "destination_name": self._get_airport_name(dest),
                "scheduled_time": f"{np.random.randint(6, 23):02d}:{np.random.randint(0, 59):02d}",
                "status": np.random.choice(["On Time", "Delayed", "Boarding", "Departed"]),
                "gate": f"{np.random.choice(['A', 'B', 'C'])}{np.random.randint(1, 20)}",
                "aircraft": np.random.choice(["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A330"])
            })
        
        return sorted(flights, key=lambda x: x["scheduled_time"])
    
    def get_airport_arrivals(self, airport_code: str) -> List[Dict]:
        """공항 도착편 조회 (시뮬레이션)"""
        flights = []
        airlines = ["KE", "OZ", "JL", "NH", "CA", "MU", "SQ", "TG"]
        origins = ["NRT", "HND", "PEK", "PVG", "SIN", "BKK", "LAX", "JFK"]
        
        for i in range(10):
            airline = np.random.choice(airlines)
            origin = np.random.choice(origins)
            flight_num = f"{airline}{np.random.randint(100, 9999)}"
            
            flights.append({
                "flight_number": flight_num,
                "airline": self._get_airline_from_code(airline),
                "origin": origin,
                "origin_name": self._get_airport_name(origin),
                "scheduled_time": f"{np.random.randint(6, 23):02d}:{np.random.randint(0, 59):02d}",
                "status": np.random.choice(["On Time", "Delayed", "Landed", "Approaching"]),
                "gate": f"{np.random.choice(['A', 'B', 'C'])}{np.random.randint(1, 20)}",
                "aircraft": np.random.choice(["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A330"])
            })
        
        return sorted(flights, key=lambda x: x["scheduled_time"])
    
    def _get_airline_from_code(self, code: str) -> str:
        """항공사 코드를 이름으로 변환"""
        airlines = {
            "KE": "대한항공",
            "OZ": "아시아나항공",
            "JL": "일본항공",
            "NH": "전일본공수",
            "CA": "중국국제항공",
            "MU": "중국동방항공",
            "SQ": "싱가포르항공",
            "TG": "타이항공",
            "AA": "아메리칸항공",
            "DL": "델타항공",
            "UA": "유나이티드항공"
        }
        return airlines.get(code, code)
    
    def _get_airport_name(self, code: str) -> str:
        """공항 코드를 이름으로 변환"""
        airports = {
            "ICN": "인천국제공항",
            "NRT": "나리타국제공항",
            "HND": "하네다공항",
            "PEK": "베이징수도국제공항",
            "PVG": "상하이푸동국제공항",
            "SIN": "싱가포르창이공항",
            "BKK": "방콕수완나품공항",
            "LAX": "로스앤젤레스국제공항",
            "JFK": "존F케네디국제공항"
        }
        return airports.get(code, code)

# FlightAware API 인스턴스
flight_api = FlightAwareAPI()

# 메인 애플리케이션
def main():
    st.markdown('<h1 class="main-title fade-in">✈️ FlightAware Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.markdown("### 🛫 검색 옵션")
        
        search_type = st.selectbox(
            "검색 유형",
            ["항공편 조회", "공항 출발편", "공항 도착편", "항공편 추적"]
        )
        
        if search_type == "항공편 조회":
            flight_number = st.text_input("항공편 번호 (예: KE001)", "KE001")
            search_button = st.button("🔍 항공편 조회", key="flight_search")
            
        elif search_type in ["공항 출발편", "공항 도착편"]:
            airport_code = st.text_input("공항 코드 (예: ICN)", "ICN").upper()
            search_button = st.button("🔍 공항 정보 조회", key="airport_search")
            
        else:  # 항공편 추적
            flight_number = st.text_input("추적할 항공편 번호", "KE001")
            search_button = st.button("📍 항공편 추적", key="track_search")
    
    # 메인 컨텐츠
    if search_type == "항공편 조회" and st.session_state.get("flight_search", False):
        display_flight_info(flight_number)
        
    elif search_type == "공항 출발편" and st.session_state.get("airport_search", False):
        display_airport_departures(airport_code)
        
    elif search_type == "공항 도착편" and st.session_state.get("airport_search", False):
        display_airport_arrivals(airport_code)
        
    elif search_type == "항공편 추적" and st.session_state.get("track_search", False):
        display_flight_tracking(flight_number)
    
    # 기본 대시보드
    if not any([st.session_state.get("flight_search", False), 
                st.session_state.get("airport_search", False), 
                st.session_state.get("track_search", False)]):
        display_dashboard()
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_flight_info(flight_number: str):
    """항공편 정보 표시"""
    st.markdown('<h2 class="section-title">📋 항공편 정보</h2>', unsafe_allow_html=True)
    
    with st.spinner("항공편 정보를 조회하는 중..."):
        time.sleep(1)  # API 호출 시뮬레이션
        flight_info = flight_api.get_flight_info(flight_number)
    
    # 항공편 기본 정보
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("항공편", flight_info["flight_number"])
    with col2:
        st.metric("항공사", flight_info["airline"])
    with col3:
        st.metric("항공기", flight_info["aircraft"])
    with col4:
        status_color = "🟢" if flight_info["status"] == "On Time" else "🟡"
        st.metric("상태", f"{status_color} {flight_info['status']}")
    
    # 출발/도착 정보
    st.markdown('<h3 class="section-title">🛫 출발 정보</h3>', unsafe_allow_html=True)
    dep_col1, dep_col2, dep_col3 = st.columns(3)
    
    with dep_col1:
        st.markdown(f"""
        <div class="flight-card">
            <h4>🏢 공항</h4>
            <p><strong>{flight_info['departure']['airport']}</strong> - {flight_info['departure']['airport_name']}</p>
            <p>{flight_info['departure']['city']}, {flight_info['departure']['country']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with dep_col2:
        st.markdown(f"""
        <div class="flight-card">
            <h4>⏰ 시간</h4>
            <p><strong>예정:</strong> {flight_info['departure']['scheduled_time']}</p>
            <p><strong>실제:</strong> {flight_info['departure']['actual_time']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with dep_col3:
        st.markdown(f"""
        <div class="flight-card">
            <h4>🚪 게이트</h4>
            <p><strong>게이트:</strong> {flight_info['departure']['gate']}</p>
            <p><strong>터미널:</strong> {flight_info['departure']['terminal']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-title">🛬 도착 정보</h3>', unsafe_allow_html=True)
    arr_col1, arr_col2, arr_col3 = st.columns(3)
    
    with arr_col1:
        st.markdown(f"""
        <div class="flight-card">
            <h4>🏢 공항</h4>
            <p><strong>{flight_info['arrival']['airport']}</strong> - {flight_info['arrival']['airport_name']}</p>
            <p>{flight_info['arrival']['city']}, {flight_info['arrival']['country']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with arr_col2:
        st.markdown(f"""
        <div class="flight-card">
            <h4>⏰ 시간</h4>
            <p><strong>예정:</strong> {flight_info['arrival']['scheduled_time']}</p>
            <p><strong>실제:</strong> {flight_info['arrival']['actual_time']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with arr_col3:
        st.markdown(f"""
        <div class="flight-card">
            <h4>🚪 게이트</h4>
            <p><strong>게이트:</strong> {flight_info['arrival']['gate']}</p>
            <p><strong>터미널:</strong> {flight_info['arrival']['terminal']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 항공편 상세 정보
    st.markdown('<h3 class="section-title">📊 항공편 상세</h3>', unsafe_allow_html=True)
    detail_col1, detail_col2, detail_col3 = st.columns(3)
    
    with detail_col1:
        st.metric("비행 시간", flight_info["duration"])
    with detail_col2:
        st.metric("거리", flight_info["distance"])
    with detail_col3:
        st.metric("현재 상태", flight_info["status"])

def display_airport_departures(airport_code: str):
    """공항 출발편 표시"""
    st.markdown(f'<h2 class="section-title">🛫 {airport_code} 출발편</h2>', unsafe_allow_html=True)
    
    with st.spinner("출발편 정보를 조회하는 중..."):
        time.sleep(1)
        departures = flight_api.get_airport_departures(airport_code)
    
    # 출발편 통계
    col1, col2, col3, col4 = st.columns(4)
    
    on_time = len([f for f in departures if f["status"] == "On Time"])
    delayed = len([f for f in departures if f["status"] == "Delayed"])
    boarding = len([f for f in departures if f["status"] == "Boarding"])
    departed = len([f for f in departures if f["status"] == "Departed"])
    
    with col1:
        st.metric("정시", on_time, "편")
    with col2:
        st.metric("지연", delayed, "편")
    with col3:
        st.metric("탑승중", boarding, "편")
    with col4:
        st.metric("출발", departed, "편")
    
    # 출발편 테이블
    df = pd.DataFrame(departures)
    st.dataframe(df, use_container_width=True)

def display_airport_arrivals(airport_code: str):
    """공항 도착편 표시"""
    st.markdown(f'<h2 class="section-title">🛬 {airport_code} 도착편</h2>', unsafe_allow_html=True)
    
    with st.spinner("도착편 정보를 조회하는 중..."):
        time.sleep(1)
        arrivals = flight_api.get_airport_arrivals(airport_code)
    
    # 도착편 통계
    col1, col2, col3, col4 = st.columns(4)
    
    on_time = len([f for f in arrivals if f["status"] == "On Time"])
    delayed = len([f for f in arrivals if f["status"] == "Delayed"])
    landed = len([f for f in arrivals if f["status"] == "Landed"])
    approaching = len([f for f in arrivals if f["status"] == "Approaching"])
    
    with col1:
        st.metric("정시", on_time, "편")
    with col2:
        st.metric("지연", delayed, "편")
    with col3:
        st.metric("착륙", landed, "편")
    with col4:
        st.metric("접근중", approaching, "편")
    
    # 도착편 테이블
    df = pd.DataFrame(arrivals)
    st.dataframe(df, use_container_width=True)

def display_flight_tracking(flight_number: str):
    """항공편 추적 표시"""
    st.markdown(f'<h2 class="section-title">📍 {flight_number} 항공편 추적</h2>', unsafe_allow_html=True)
    
    # 항공편 추적 맵
    st.markdown('<h3 class="section-title">🗺️ 실시간 추적</h3>', unsafe_allow_html=True)
    
    # 시뮬레이션된 항공편 위치 데이터
    m = folium.Map(
        location=[35.5, 139.0],  # 도쿄 근처
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # 항공편 경로 시뮬레이션
    route_coords = [
        [37.5665, 126.9780],  # 서울
        [36.0, 135.0],        # 중간 지점
        [35.5, 139.0]         # 도쿄
    ]
    
    # 경로 그리기
    folium.PolyLine(
        route_coords,
        color='blue',
        weight=3,
        opacity=0.8
    ).add_to(m)
    
    # 출발지 마커
    folium.Marker(
        [37.5665, 126.9780],
        popup='서울 (ICN)',
        icon=folium.Icon(color='green', icon='plane')
    ).add_to(m)
    
    # 도착지 마커
    folium.Marker(
        [35.5, 139.0],
        popup='도쿄 (NRT)',
        icon=folium.Icon(color='red', icon='plane')
    ).add_to(m)
    
    # 현재 위치 마커 (시뮬레이션)
    current_lat = 36.0 + np.random.uniform(-0.5, 0.5)
    current_lon = 135.0 + np.random.uniform(-0.5, 0.5)
    
    folium.Marker(
        [current_lat, current_lon],
        popup=f'{flight_number} 현재 위치',
        icon=folium.Icon(color='blue', icon='plane', prefix='fa')
    ).add_to(m)
    
    st_folium(m, width=700, height=500)
    
    # 추적 정보
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("현재 고도", "35,000 ft")
    with col2:
        st.metric("현재 속도", "850 km/h")
    with col3:
        st.metric("남은 거리", "650 km")

def display_dashboard():
    """기본 대시보드 표시"""
    st.markdown('<h2 class="section-title">📊 항공 현황 대시보드</h2>', unsafe_allow_html=True)
    
    # 주요 공항 현황
    st.markdown('<h3 class="section-title">🏢 주요 공항 현황</h3>', unsafe_allow_html=True)
    
    airports = ["ICN", "NRT", "HND", "PEK", "PVG"]
    airport_data = []
    
    for airport in airports:
        departures = flight_api.get_airport_departures(airport)
        arrivals = flight_api.get_airport_arrivals(airport)
        
        airport_data.append({
            "공항": airport,
            "출발편": len(departures),
            "도착편": len(arrivals),
            "정시율": f"{np.random.randint(85, 98)}%",
            "지연율": f"{np.random.randint(2, 15)}%"
        })
    
    df = pd.DataFrame(airport_data)
    st.dataframe(df, use_container_width=True)
    
    # 항공사별 통계
    st.markdown('<h3 class="section-title">✈️ 항공사별 통계</h3>', unsafe_allow_html=True)
    
    airlines = ["대한항공", "아시아나항공", "일본항공", "전일본공수", "중국국제항공"]
    flights_count = [np.random.randint(50, 200) for _ in airlines]
    
    fig = px.bar(
        x=airlines,
        y=flights_count,
        title="항공사별 일일 운항편 수",
        color=flights_count,
        color_continuous_scale="viridis"
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 시간대별 운항 현황
    st.markdown('<h3 class="section-title">⏰ 시간대별 운항 현황</h3>', unsafe_allow_html=True)
    
    hours = list(range(24))
    flight_counts = [np.random.randint(10, 50) for _ in hours]
    
    fig = px.line(
        x=hours,
        y=flight_counts,
        title="시간대별 운항편 수",
        markers=True
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis_title="시간",
        yaxis_title="운항편 수"
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
